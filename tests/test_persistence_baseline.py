"""持久化基线测试。"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from backend.application.services.image_job_application_service import ImageJobApplicationService
from backend.infrastructure.persistence import (
    get_concept_repository,
    get_history_repository,
    get_image_job_repository,
    get_publish_repository,
    init_database_schema,
    reset_database_engine,
    reset_repository_singletons,
)


@pytest.fixture
def isolated_database(tmp_path: Path):
    """为每个用例提供隔离的 SQLite 数据库。"""
    db_path = tmp_path / "test_redink.db"
    os.environ["REDINK_DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    reset_repository_singletons()
    reset_database_engine()
    init_database_schema()
    yield
    reset_repository_singletons()
    reset_database_engine()
    os.environ.pop("REDINK_DATABASE_URL", None)


def test_history_repository_crud(isolated_database):
    """历史仓储应支持基础 CRUD 与统计。"""
    repo = get_history_repository()
    outline = {
        "raw": "测试大纲",
        "pages": [
            {"index": 0, "type": "cover", "content": "封面"},
            {"index": 1, "type": "content", "content": "正文"},
        ],
    }

    record_id = repo.create_record("测试主题", outline, task_id="task_1")
    assert record_id

    detail = repo.get_record(record_id)
    assert detail is not None
    assert detail["title"] == "测试主题"
    assert detail["outline"]["raw"] == "测试大纲"

    updated = repo.update_record(
        record_id,
        images={"task_id": "task_1", "generated": ["0.png", "1.png"]},
        status="completed",
        thumbnail="0.png",
    )
    assert updated is True

    listing = repo.list_records(page=1, page_size=10, status=None)
    assert listing["total"] == 1
    assert listing["records"][0]["status"] == "completed"

    stats = repo.get_statistics()
    assert stats["total"] == 1
    assert stats["by_status"].get("completed") == 1


def test_concept_and_publish_repositories(isolated_database):
    """概念仓储与发布仓储应可正常写入和查询。"""
    concept_repo = get_concept_repository()
    publish_repo = get_publish_repository()

    concept_id = concept_repo.create_record(
        title="概念主题",
        article="这是一段用于测试的文章正文",
        task_id="concept_task_1",
        style="blueprint",
    )
    assert concept_id

    concept_repo.update_record(
        concept_id,
        status="completed",
        image_count=3,
        pipeline_data={"generate": {"results": ["a.png", "b.png", "c.png"]}},
    )
    concept_detail = concept_repo.get_record(concept_id)
    assert concept_detail is not None
    assert concept_detail["status"] == "completed"
    assert concept_detail["image_count"] == 3

    publish_id = publish_repo.create_record(
        title="发布标题",
        content="发布正文",
        images=["/api/images/task/0.png"],
        tags=["测试"],
        status="pending",
    )
    assert publish_id > 0

    publish_repo.update_record(publish_id, status="success", message="发布成功", post_url="https://example.com/post/1")
    publish_detail = publish_repo.get_record(publish_id)
    assert publish_detail is not None
    assert publish_detail["status"] == "success"
    assert publish_detail["post_url"] == "https://example.com/post/1"


class _FakeImageGenerationService:
    """用于测试的图片生成服务替身。"""

    def generate_images(self, pages, task_id=None, **kwargs):
        for page in pages:
            yield {
                "event": "complete",
                "data": {
                    "index": page["index"],
                    "image_url": f"/api/images/{task_id or 'fake_task'}/{page['index']}.png",
                },
            }
        yield {
            "event": "finish",
            "data": {
                "task_id": task_id or "fake_task",
                "success": True,
            },
        }


def test_image_job_application_service(isolated_database):
    """异步图片任务应用服务应将状态写入仓储。"""
    repo = get_image_job_repository()
    app_service = ImageJobApplicationService(_FakeImageGenerationService(), repo)

    pages = [
        {"index": 0, "type": "cover", "content": "封面"},
        {"index": 1, "type": "content", "content": "正文"},
    ]
    job_id = app_service.create_job(
        pages=pages,
        task_id="job_task_1",
        full_outline="测试大纲",
        user_topic="测试主题",
    )
    assert job_id

    # 轮询等待任务完成
    deadline = time.time() + 5
    final = None
    while time.time() < deadline:
        final = app_service.get_job(job_id)
        if final and final.get("status") in {"success", "failed", "cancelled"}:
            break
        time.sleep(0.05)

    assert final is not None
    assert final["status"] == "success"
    assert final["completed_pages"] == 2
    assert final["failed_pages"] == 0
    assert len(final.get("items") or []) == 2


def test_database_url_resolution_and_fallback(monkeypatch, tmp_path: Path):
    """测试数据库连接串解析与回退逻辑。"""
    from backend.infrastructure.persistence.session import get_database_url

    monkeypatch.delenv("REDINK_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # 1. 默认回退
    default_url = get_database_url()
    assert "sqlite:///" in default_url

    # 2. 回退到 DATABASE_URL
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test_fallback.db")
    assert get_database_url() == "sqlite:///test_fallback.db"

    # 3. 优先使用 REDINK_DATABASE_URL
    monkeypatch.setenv("REDINK_DATABASE_URL", "sqlite:///test_redink.db")
    assert get_database_url() == "sqlite:///test_redink.db"

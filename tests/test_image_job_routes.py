"""异步图片任务路由测试。"""

from __future__ import annotations

from flask import Flask

from backend.routes import image_job_routes


class _FakeImageJobService:
    """用于路由测试的图片任务服务替身。"""

    def __init__(self) -> None:
        self.created_payload: dict[str, object] = {}

    def create_job(
        self,
        *,
        pages: list[dict[str, object]],
        task_id: str | None = None,
        full_outline: str = "",
        user_images_base64: list[str] | None = None,
        user_topic: str = "",
        user_prompt: str = "",
        system_prompt: str = "",
        record_id: str | None = None,
    ) -> str:
        self.created_payload = {
            "pages": pages,
            "task_id": task_id,
            "full_outline": full_outline,
            "user_images": user_images_base64 or [],
            "user_topic": user_topic,
            "user_prompt": user_prompt,
            "system_prompt": system_prompt,
            "record_id": record_id,
        }
        return "job_test_1"

    def get_job(self, job_id: str):
        if job_id != "job_test_1":
            return None
        return {
            "id": "job_test_1",
            "status": "queued",
            "items": [{"page_index": 0, "status": "queued"}],
            "total_pages": 1,
            "completed_pages": 0,
            "failed_pages": 0,
        }

    def list_jobs(self, page: int = 1, page_size: int = 20, status: str | None = None):
        return {
            "records": [{"id": "job_test_1", "status": status or "queued"}],
            "total": 1,
            "page": page,
            "page_size": page_size,
            "total_pages": 1,
        }

    def cancel_job(self, job_id: str) -> bool:
        return job_id == "job_test_1"


def _build_client(monkeypatch):
    fake_service = _FakeImageJobService()
    monkeypatch.setattr(image_job_routes, "image_job_app_service", fake_service)

    app = Flask(__name__)
    app.register_blueprint(image_job_routes.create_image_job_blueprint(), url_prefix="/api")
    return app.test_client(), fake_service


def test_image_job_routes_happy_path(monkeypatch):
    """应支持创建、查询、列表和取消任务。"""
    client, fake_service = _build_client(monkeypatch)
    payload = {
        "pages": [{"index": 0, "type": "cover", "content": "封面"}],
        "task_id": "task_1",
        "record_id": "rec_123",
        "full_outline": "测试大纲",
        "user_topic": "测试主题",
        "user_prompt": "用户提示词",
        "system_prompt": "系统提示词",
    }

    create_resp = client.post("/api/image-jobs", json=payload)
    assert create_resp.status_code == 200
    create_data = create_resp.get_json()
    assert create_data["success"] is True
    assert create_data["job_id"] == "job_test_1"
    assert fake_service.created_payload["user_prompt"] == "用户提示词"
    assert fake_service.created_payload["record_id"] == "rec_123"

    get_resp = client.get("/api/image-jobs/job_test_1")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["success"] is True

    list_resp = client.get("/api/image-jobs?page=1&page_size=10&status=queued")
    assert list_resp.status_code == 200
    list_data = list_resp.get_json()
    assert list_data["success"] is True
    assert list_data["total"] == 1

    cancel_resp = client.post("/api/image-jobs/job_test_1/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.get_json()["cancel_requested"] is True


def test_image_job_routes_invalid_payload(monkeypatch):
    """参数不合法时应返回 400。"""
    client, _ = _build_client(monkeypatch)

    resp = client.post("/api/image-jobs", json={"pages": []})
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False

    resp2 = client.post("/api/image-jobs", json={"pages": [{"index": 0, "type": "cover"}]})
    assert resp2.status_code == 400
    assert resp2.get_json()["success"] is False

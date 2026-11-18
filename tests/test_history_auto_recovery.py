"""历史记录任务与图片自动挽救机制测试。"""

import json
from pathlib import Path

from backend.infrastructure.services.history import HistoryService


def test_history_service_auto_recover_missing_task_id(tmp_path: Path, monkeypatch):
    """当历史记录因意外中断缺少 task_id 时，能从本地 task 目录自动挽救图片数据。"""
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)
    (history_dir / "index.json").write_text('{"records": []}', encoding="utf-8")

    # 创建一个模拟的 task 目录及图片
    task_dir = history_dir / "task_mock123"
    task_dir.mkdir()
    (task_dir / "0.png").write_bytes(b"image 0")
    (task_dir / "1.png").write_bytes(b"image 1")

    # 实例化 HistoryService
    monkeypatch.setenv("HISTORY_STORAGE_MODE", "local")
    service = HistoryService()
    service.history_dir = str(history_dir)
    service.index_file = str(history_dir / "index.json")

    # 模拟一份缺少 task_id 的历史记录（如网络报错或未落盘保存时）
    record_id = "test_rec_1"
    record_file = history_dir / f"{record_id}.json"
    raw_record = {
        "id": record_id,
        "title": "游戏主机配置",
        "outline": {
            "topic": "游戏主机配置",
            "pages": [
                {"index": 0, "type": "cover", "content": "封面"},
                {"index": 1, "type": "content", "content": "内容页"},
            ],
        },
        "images": {
            "task_id": None,
            "generated": [],
        },
        "content": {
            "titles": ["游戏主机配置"],
            "copywriting": "配置推荐",
            "tags": ["游戏主机"],
        },
    }
    record_file.write_text(json.dumps(raw_record, ensure_ascii=False), encoding="utf-8")

    # 获取记录时应能自动找回 task_mock123 并挂载生成的图片列表
    loaded = service.get_record(record_id)
    assert loaded is not None
    assert loaded["images"]["task_id"] == "task_mock123"
    assert loaded["images"]["generated"] == ["0.png", "1.png"]
    assert loaded["thumbnail"] == "thumb_0.png"


def test_history_service_does_not_steal_claimed_task_or_draft(tmp_path: Path, monkeypatch):
    """验证已被其他记录占用的 task_id 不会被抢占，且草稿状态记录不会抢占任务"""
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True)

    task_dir = history_dir / "task_claimed999"
    task_dir.mkdir()
    (task_dir / "0.png").write_bytes(b"image 0")
    (task_dir / "1.png").write_bytes(b"image 1")

    # index.json 中声明 task_claimed999 属于 record_owner
    index_data = {
        "records": [
            {
                "id": "record_owner",
                "title": "已完成作品",
                "task_id": "task_claimed999",
                "status": "completed"
            }
        ]
    }
    (history_dir / "index.json").write_text(json.dumps(index_data), encoding="utf-8")

    monkeypatch.setenv("HISTORY_STORAGE_MODE", "local")
    service = HistoryService()
    service.history_dir = str(history_dir)
    service.index_file = str(history_dir / "index.json")

    # 1. 尝试让另一个丢失 task_id 的非草稿记录挽救：由于 task_claimed999 已被占用，不能抢占
    rec_other = {
        "id": "rec_other",
        "title": "新文章",
        "status": "completed",
        "outline": {
            "topic": "新文章",
            "pages": [{"index": 0}, {"index": 1}]
        },
        "images": {"task_id": None, "generated": []}
    }
    (history_dir / "rec_other.json").write_text(json.dumps(rec_other), encoding="utf-8")

    loaded_other = service.get_record("rec_other")
    assert loaded_other is not None
    assert loaded_other["images"]["task_id"] is None

    # 2. 草稿记录 (status="draft") 不会自动挂载
    rec_draft = {
        "id": "rec_draft",
        "title": "草稿文章",
        "status": "draft",
        "outline": {
            "topic": "草稿文章",
            "pages": [{"index": 0}, {"index": 1}]
        },
        "images": {"task_id": None, "generated": []}
    }
    (history_dir / "rec_draft.json").write_text(json.dumps(rec_draft), encoding="utf-8")

    loaded_draft = service.get_record("rec_draft")
    assert loaded_draft is not None
    assert loaded_draft["images"]["task_id"] is None


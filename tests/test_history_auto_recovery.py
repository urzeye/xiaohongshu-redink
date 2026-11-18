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

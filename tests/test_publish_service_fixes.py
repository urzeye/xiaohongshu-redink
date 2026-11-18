import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from backend.infrastructure.services.publish import PublishService


def test_get_local_cookies_status_missing(tmp_path):
    svc = PublishService(gateway=MagicMock())
    svc.project_root = tmp_path
    status = svc._get_local_cookies_status()
    assert status["has_file"] is False
    assert status["logged_in"] is False
    assert status["creator_authorized"] is False


def test_get_local_cookies_status_main_authorized(tmp_path):
    svc = PublishService(gateway=MagicMock())
    svc.project_root = tmp_path
    cookies_path = tmp_path / "cookies.json"
    cookies_path.write_text(
        json.dumps({
            "version": 1,
            "cookies": [
                {"name": "web_session", "value": "xyz", "domain": ".xiaohongshu.com"},
                {"name": "a1", "value": "abc", "domain": ".xiaohongshu.com"}
            ]
        }),
        encoding="utf-8"
    )

    status = svc._get_local_cookies_status()
    assert status["has_file"] is True
    assert status["logged_in"] is True
    assert status["creator_authorized"] is True
    assert "就绪" in status["message"]


def test_get_local_cookies_status_full_authorized(tmp_path):
    svc = PublishService(gateway=MagicMock())
    svc.project_root = tmp_path
    cookies_path = tmp_path / "cookies.json"
    cookies_path.write_text(
        json.dumps({
            "version": 1,
            "cookies": [
                {"name": "web_session", "value": "xyz", "domain": ".xiaohongshu.com"},
                {"name": "galaxy_creator_session_id", "value": "creator_xyz", "domain": "creator.xiaohongshu.com"}
            ]
        }),
        encoding="utf-8"
    )

    status = svc._get_local_cookies_status()
    assert status["has_file"] is True
    assert status["logged_in"] is True
    assert status["creator_authorized"] is True
    assert "就绪" in status["message"]


def test_publish_intercepts_when_not_logged_in(tmp_path):
    svc = PublishService(gateway=MagicMock())
    svc.project_root = tmp_path
    # 模拟图片存在
    img = tmp_path / "test.png"
    img.write_text("fake image")

    result = asyncio.run(svc.publish(
        title="测试标题",
        content="测试正文",
        images=[str(img)]
    ))

    assert result["success"] is False
    assert "未登录" in result["error"] or "失效" in result["error"]
    assert "未登录" in result["message"] or "失效" in result["message"]


def test_start_service_delegates_to_gateway():
    gateway = MagicMock()
    gateway.start_service.return_value = {
        "success": True,
        "running": True,
        "message": "VibeSurf 服务已启动"
    }
    svc = PublishService(gateway=gateway)

    result = asyncio.run(svc.start_service())
    assert result["success"] is True
    assert result["running"] is True
    gateway.start_service.assert_called_once()


def test_sync_creator_session_cookie(tmp_path):
    svc = PublishService(gateway=MagicMock())
    svc.project_root = tmp_path
    cookies_path = tmp_path / "cookies.json"
    cookies_path.write_text(
        json.dumps({
            "version": 1,
            "cookies": [
                {"name": "web_session", "value": "test_web_session_val", "domain": ".xiaohongshu.com"}
            ]
        }),
        encoding="utf-8"
    )

    synced = svc._sync_creator_session_cookie()
    assert synced is True

    updated_data = json.loads(cookies_path.read_text(encoding="utf-8"))
    cookies = updated_data.get("cookies", [])
    galaxy_cookies = [c for c in cookies if c.get("name") == "galaxy_creator_session_id"]
    assert len(galaxy_cookies) == 2
    assert all(c["value"] == "test_web_session_val" for c in galaxy_cookies)



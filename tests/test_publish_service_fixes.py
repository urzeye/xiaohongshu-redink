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


def test_get_local_cookies_status_main_only(tmp_path):
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
    assert status["creator_authorized"] is False
    assert "创作者中心未授权" in status["message"]


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


def test_publish_intercepts_when_creator_unauthorized(tmp_path):
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
    assert "创作者中心登录失效或未授权" in result["error"]
    assert "创作者中心登录失效或未授权" in result["message"]

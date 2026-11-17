"""
Unit tests for MCPManager.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from backend.utils.mcp_manager import MCPManager


def test_mcp_extract_text_and_image():
    manager = MCPManager()

    content = [
        {"type": "text", "text": "请用小红书 App 扫码登录"},
        {"type": "image", "mimeType": "image/png", "data": "iVBORw0KGgoAAAANSUhEUgAA"},
    ]

    text = manager._extract_text_from_content(content)
    assert text == "请用小红书 App 扫码登录"

    img = manager._extract_image_from_content(content)
    assert img is not None
    assert img["mime_type"] == "image/png"
    assert img["data"] == "iVBORw0KGgoAAAANSUhEUgAA"
    assert img["data_url"] == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA"


def test_mcp_normalize_response_with_qrcode():
    manager = MCPManager()

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [
                {"type": "text", "text": "扫码登录提示"},
                {"type": "image", "mimeType": "image/png", "data": "BASE64DATA"},
            ]
        },
    }

    normalized = manager._normalize_mcp_tool_response(payload, "get_login_qrcode")
    assert normalized["success"] is True
    assert normalized["message"] == "扫码登录提示"
    assert "image" in normalized
    assert normalized["qrcode"] == "data:image/png;base64,BASE64DATA"


def test_mcp_normalize_error_response():
    manager = MCPManager()

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32602,
            "message": "unknown tool 'open_login_page'"
        }
    }

    normalized = manager._normalize_mcp_tool_response(payload, "open_login_page")
    assert normalized["success"] is False
    assert "unknown tool" in normalized["error"]


def test_mcp_initialize_stateless():
    async def _run():
        manager = MCPManager()
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.headers = {}  # No Mcp-Session-Id in stateless mode
        mock_client.post.return_value = mock_resp

        await manager._mcp_initialize(mock_client)
        assert manager._session_id == "stateless"
        # Should not call notifications/initialized when stateless
        assert mock_client.post.call_count == 1

    asyncio.run(_run())

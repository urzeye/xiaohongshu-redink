"""配置管理与预设路由测试。"""

import os
from flask import Flask
from backend.routes.config_routes import create_config_blueprint


def _build_test_client():
    app = Flask(__name__)
    app.register_blueprint(create_config_blueprint(), url_prefix="/api")
    return app.test_client()


def _get_auth_headers():
    token = os.environ.get("REDINK_AUTH_TOKEN", "").strip()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def test_get_config_and_reload():
    client = _build_test_client()
    headers = _get_auth_headers()

    # 1. 测试 GET /api/config
    res = client.get("/api/config", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "config" in data
    assert "text_generation" in data["config"]
    assert "image_generation" in data["config"]
    assert "search" in data["config"]

    # 验证预设已加载
    text_providers = data["config"]["text_generation"]["providers"]
    assert "deepseek" in text_providers or "default" in text_providers

    # 2. 测试 POST /api/config/reload
    reload_res = client.post("/api/config/reload", headers=headers)
    assert reload_res.status_code == 200
    reload_data = reload_res.get_json()
    assert reload_data["success"] is True


def test_reset_defaults():
    client = _build_test_client()
    headers = _get_auth_headers()

    res = client.post("/api/config/reset-defaults", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True

    text_providers = data["config"]["text_generation"]["providers"]
    # 验证核心国内大模型预设已包含
    assert "deepseek" in text_providers
    assert "qwen" in text_providers
    assert "zhipu" in text_providers
    assert "ark_doubao" in text_providers

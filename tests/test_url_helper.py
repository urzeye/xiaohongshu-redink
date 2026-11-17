"""测试 URL 解析与端点拼接工具函数及相关测试连接逻辑。"""

from unittest.mock import MagicMock, patch

import pytest

from backend.routes.config_routes import _test_image_api, _test_openai_compatible
from backend.utils.url_helper import build_models_url, resolve_api_url


class TestResolveApiUrl:
    """测试 resolve_api_url 函数"""

    def test_standard_openai_urls(self):
        # 基础 OpenAI 域名 + 默认 /v1/images/generations
        assert (
            resolve_api_url("https://api.openai.com", "/v1/images/generations")
            == "https://api.openai.com/v1/images/generations"
        )
        # 已经带 /v1 的 base_url，避免重复 /v1/v1/
        assert (
            resolve_api_url("https://api.openai.com/v1", "/v1/images/generations")
            == "https://api.openai.com/v1/images/generations"
        )
        # 末尾斜杠容错
        assert (
            resolve_api_url("https://api.openai.com/v1/", "/v1/images/generations")
            == "https://api.openai.com/v1/images/generations"
        )
        # base_url 带 /v1，endpoint 未带 /v1
        assert (
            resolve_api_url("https://api.openai.com/v1", "/images/generations")
            == "https://api.openai.com/v1/images/generations"
        )

    def test_volcano_ark_urls(self):
        # 火山方舟 /api/v3 + /images/generations
        assert (
            resolve_api_url(
                "https://ark.cn-beijing.volces.com/api/v3", "/images/generations"
            )
            == "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        )
        # 用户未改默认 /v1/images/generations，自动去除重复 /v1
        assert (
            resolve_api_url(
                "https://ark.cn-beijing.volces.com/api/v3", "/v1/images/generations"
            )
            == "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        )
        # 火山方舟聊天端点
        assert (
            resolve_api_url(
                "https://ark.cn-beijing.volces.com/api/v3", "/v1/chat/completions"
            )
            == "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        )

    def test_other_provider_urls(self):
        # DashScope 兼容模式
        assert (
            resolve_api_url(
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "/v1/images/generations",
            )
            == "https://dashscope.aliyuncs.com/compatible-mode/v1/images/generations"
        )
        # SiliconFlow
        assert (
            resolve_api_url(
                "https://api.siliconflow.cn/v1", "/v1/images/generations"
            )
            == "https://api.siliconflow.cn/v1/images/generations"
        )

    def test_alias_endpoints(self):
        # 'images' 简写
        assert (
            resolve_api_url("https://api.openai.com", "images")
            == "https://api.openai.com/v1/images/generations"
        )
        # 'chat' 简写
        assert (
            resolve_api_url("https://api.openai.com", "chat")
            == "https://api.openai.com/v1/chat/completions"
        )

    def test_empty_or_none_inputs(self):
        # 空 base_url 使用默认 openai
        assert (
            resolve_api_url(None, "/v1/images/generations")
            == "https://api.openai.com/v1/images/generations"
        )


class TestBuildModelsUrl:
    """测试 build_models_url 函数"""

    def test_models_urls(self):
        assert (
            build_models_url("https://api.openai.com")
            == "https://api.openai.com/v1/models"
        )
        assert (
            build_models_url("https://api.openai.com/v1")
            == "https://api.openai.com/v1/models"
        )
        assert (
            build_models_url("https://ark.cn-beijing.volces.com/api/v3")
            == "https://ark.cn-beijing.volces.com/api/v3/models"
        )
        assert (
            build_models_url("https://dashscope.aliyuncs.com/compatible-mode/v1")
            == "https://dashscope.aliyuncs.com/compatible-mode/v1/models"
        )


class TestTestProviderConnection:
    """测试服务商连接测试函数"""

    @patch("requests.get")
    def test_image_api_volcano_ark_connection_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        config = {
            "api_key": "ark-test-key",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "model": "ep-test-model",
        }
        res = _test_image_api(config)
        assert res["success"] is True

        # 验证请求到了火山方舟正确的 models 路径，没有拼错成 /api/v3/v1/models
        mock_get.assert_called_once_with(
            "https://ark.cn-beijing.volces.com/api/v3/models",
            headers={"Authorization": "Bearer ark-test-key"},
            timeout=30,
        )

    @patch("requests.get")
    def test_image_api_fallback_on_404(self, mock_get):
        # 第一次返回 404，第二次备用路径返回 200
        resp_404 = MagicMock(status_code=404)
        resp_200 = MagicMock(status_code=200)
        mock_get.side_effect = [resp_404, resp_200]

        config = {
            "api_key": "test-key",
            "base_url": "https://custom.provider.com/v1",
            "model": "test-model",
        }
        res = _test_image_api(config)
        assert res["success"] is True
        assert mock_get.call_count == 2

    @patch("requests.post")
    def test_openai_compatible_volcano_ark_text_test(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "你好，RedInk"}}]
        }
        mock_post.return_value = mock_response

        config = {
            "api_key": "ark-text-key",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "model": "doubao-pro-32k",
        }
        res = _test_openai_compatible(config, "test")
        assert res["success"] is True
        # 验证文本测试也是请求到 /api/v3/chat/completions 而不是 /api/v3/v1/chat/completions
        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert call_url == "https://ark.cn-beijing.volces.com/api/v3/chat/completions"


class TestConfigApiRoute:
    """测试 /api/config/test 路由"""

    @patch("requests.get")
    def test_route_image_api_volcano_test(self, mock_get, monkeypatch):
        from flask import Flask
        from backend.routes.config_routes import create_config_blueprint

        monkeypatch.setenv("REDINK_AUTH_TOKEN", "")

        app = Flask(__name__)
        app.register_blueprint(create_config_blueprint(), url_prefix="/api")
        client = app.test_client()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        payload = {
            "type": "image_api",
            "api_key": "ark-test-key",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "model": "ep-test-model",
        }
        response = client.post("/api/config/test", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        mock_get.assert_called_once_with(
            "https://ark.cn-beijing.volces.com/api/v3/models",
            headers={"Authorization": "Bearer ark-test-key"},
            timeout=30,
        )

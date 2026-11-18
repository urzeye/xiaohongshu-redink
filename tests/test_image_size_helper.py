"""图片尺寸与宽高比解析测试。"""

from backend.utils.image_size_helper import (
    resolve_image_dimensions,
    normalize_aspect_ratio,
    is_volcano_ark,
    is_siliconflow,
    is_dall_e_3,
)
from backend.infrastructure.generators.image_api import ImageApiGenerator


def test_normalize_aspect_ratio():
    assert normalize_aspect_ratio("3:4") == "3:4"
    assert normalize_aspect_ratio("3：4") == "3:4"
    assert normalize_aspect_ratio("3/4") == "3:4"
    assert normalize_aspect_ratio("") == "3:4"
    assert normalize_aspect_ratio(None) == "3:4"


def test_volcano_ark_size_resolution():
    base_url = "https://ark.cn-beijing.volces.com/api/v3"
    assert is_volcano_ark(base_url) is True

    # 默认 2K，3:4 必须是 1728x2304
    size_3_4 = resolve_image_dimensions("3:4", tier="2K", base_url=base_url)
    assert size_3_4 == "1728x2304"

    # 1:1 必须是 2048x2048
    size_1_1 = resolve_image_dimensions("1:1", tier="2K", base_url=base_url)
    assert size_1_1 == "2048x2048"

    # 4:3 必须是 2304x1728
    size_4_3 = resolve_image_dimensions("4:3", tier="2K", base_url=base_url)
    assert size_4_3 == "2304x1728"

    # 9:16 必须是 1440x2560
    size_9_16 = resolve_image_dimensions("9:16", tier="2K", base_url=base_url)
    assert size_9_16 == "1440x2560"


def test_dall_e_3_size_resolution():
    assert is_dall_e_3("dall-e-3") is True
    # 竖版 -> 1024x1792
    assert resolve_image_dimensions("3:4", model="dall-e-3") == "1024x1792"
    assert resolve_image_dimensions("9:16", model="dall-e-3") == "1024x1792"
    # 横版 -> 1792x1024
    assert resolve_image_dimensions("16:9", model="dall-e-3") == "1792x1024"
    assert resolve_image_dimensions("4:3", model="dall-e-3") == "1792x1024"
    # 方形 -> 1024x1024
    assert resolve_image_dimensions("1:1", model="dall-e-3") == "1024x1024"


def test_image_api_generator_payload_for_volcano(monkeypatch):
    """测试 ImageApiGenerator 在火山引擎配置下正确发送 3:4 尺寸"""
    captured_payload = {}

    def fake_post(url, headers, json, timeout):
        nonlocal captured_payload
        captured_payload = json
        class FakeResponse:
            status_code = 200
            def json(self):
                return {"data": [{"b64_json": "aGVsbG8="}]}
        return FakeResponse()

    monkeypatch.setattr("requests.post", fake_post)

    config = {
        "api_key": "test_key",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "ep-test-endpoint",
        "endpoint_type": "/images/generations",
        "default_aspect_ratio": "3:4",
        "use_size_tag": False,
    }
    generator = ImageApiGenerator(config)
    generator.generate_image("生成测试提示词", aspect_ratio="3:4")

    # 关键断言：size 必须是 1728x2304，绝不能是 1024x1024
    assert captured_payload["aspect_ratio"] == "3:4"
    assert captured_payload["size"] == "1728x2304"
    assert captured_payload["image_size"] == "1728x2304"

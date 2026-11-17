"""搜索路由测试。"""

from flask import Flask

from backend.routes import search_routes


class _FakeSearchApplicationService:
    """用于路由测试的搜索应用服务替身。"""

    def build_provider_status(self, provider_name=None):
        return {
            "active_provider": "bing",
            "provider": provider_name or "bing",
            "enabled": True,
            "configured": True,
        }

    def is_valid_http_url(self, url: str) -> bool:
        return url.startswith("http://") or url.startswith("https://")

    def get_search_provider_config(self, provider_name=None, require_enabled=True):
        if provider_name == "disabled":
            raise ValueError("服务商未启用")
        return {"type": "bing", "enabled": True}

    def scrape_url(self, url: str, provider_name=None, registry=None):
        return {
            "success": True,
            "data": {
                "title": "示例标题",
                "content": "示例正文",
                "word_count": 4,
                "url": url,
            },
        }


def _build_client(monkeypatch):
    monkeypatch.setattr(search_routes, "search_application_service", _FakeSearchApplicationService())

    app = Flask(__name__)
    app.register_blueprint(search_routes.create_search_blueprint(), url_prefix="/api")
    return app.test_client()


def test_search_status_and_scrape_success(monkeypatch):
    """应返回状态并支持抓取。"""
    client = _build_client(monkeypatch)

    status_resp = client.get("/api/search/status")
    assert status_resp.status_code == 200
    status_data = status_resp.get_json()
    assert status_data["success"] is True
    assert status_data["provider"] == "bing"

    scrape_resp = client.post("/api/search/scrape", json={"url": "https://example.com"})
    assert scrape_resp.status_code == 200
    scrape_data = scrape_resp.get_json()
    assert scrape_data["success"] is True
    assert scrape_data["data"]["url"] == "https://example.com"


def test_search_scrape_invalid_url(monkeypatch):
    """非法 URL 应返回 400。"""
    client = _build_client(monkeypatch)

    resp = client.post("/api/search/scrape", json={"url": "ftp://example.com"})
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False

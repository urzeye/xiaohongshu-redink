"""API 认证与回环放行中间件测试。"""

from flask import Flask, jsonify
from backend.middleware import authenticate_request


def create_test_app():
    app = Flask(__name__)

    @app.before_request
    def _guard():
        return authenticate_request(exempt_paths={"/api/health"})

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/api/images/task_1/0.png")
    def get_image():
        return jsonify({"image": "data"})

    @app.route("/api/post_data", methods=["POST"])
    def post_data():
        return jsonify({"saved": True})

    return app


def test_auth_disabled_by_default(monkeypatch):
    monkeypatch.delenv("REDINK_AUTH_TOKEN", raising=False)
    app = create_test_app()
    client = app.test_client()

    res = client.get("/api/images/task_1/0.png")
    assert res.status_code == 200


def test_auth_enabled_with_bearer_token(monkeypatch):
    monkeypatch.setenv("REDINK_AUTH_TOKEN", "secret123")
    app = create_test_app()
    client = app.test_client()

    # 无 token 时 POST 接口应 401
    res = client.post("/api/post_data", environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert res.status_code == 401

    # 带 Bearer token 时应 200
    res = client.post(
        "/api/post_data",
        headers={"Authorization": "Bearer secret123"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"}
    )
    assert res.status_code == 200


def test_auth_image_access_token_query_param(monkeypatch):
    monkeypatch.setenv("REDINK_AUTH_TOKEN", "secret123")
    app = create_test_app()
    client = app.test_client()

    # 外部 IP 带 query token 应 200
    res = client.get(
        "/api/images/task_1/0.png?access_token=secret123",
        environ_base={"REMOTE_ADDR": "192.168.1.100"}
    )
    assert res.status_code == 200

    # 外部 IP 不带 token 应 401
    res = client.get(
        "/api/images/task_1/0.png",
        environ_base={"REMOTE_ADDR": "192.168.1.100"}
    )
    assert res.status_code == 401


def test_auth_image_loopback_exemption(monkeypatch):
    monkeypatch.setenv("REDINK_AUTH_TOKEN", "secret123")
    app = create_test_app()
    client = app.test_client()

    # 127.0.0.1 本地回环访问图片，即便无 query token 也能正常访问，杜绝客户端裂图
    res = client.get(
        "/api/images/task_1/0.png",
        environ_base={"REMOTE_ADDR": "127.0.0.1"}
    )
    assert res.status_code == 200

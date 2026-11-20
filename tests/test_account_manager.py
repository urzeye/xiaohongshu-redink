import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.infrastructure.services.account_manager import XiaohongshuAccountManager


@pytest.fixture(autouse=True)
def mock_mcp():
    with patch("backend.infrastructure.services.account_manager.mcp_manager") as mock:
        mock.is_running.return_value = False
        yield mock


@pytest.fixture
def mock_env(tmp_path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    data_dir = tmp_path / "data" / "xiaohongshu"
    data_dir.mkdir(parents=True)

    # 创建初始 cookies.json
    cookies_data = {
        "version": 2,
        "seed": 123456,
        "saved_at": "2026-11-20T00:00:00Z",
        "cookies": [
            {"name": "web_session", "value": "test_session_1", "domain": ".xiaohongshu.com"},
            {"name": "a1", "value": "test_a1_1", "domain": ".xiaohongshu.com"}
        ]
    }
    with open(project_root / "cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies_data, f)
    with open(data_dir / "cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies_data, f)

    return project_root, data_dir


def test_auto_migration(mock_env):
    project_root, data_dir = mock_env

    with patch.object(
        XiaohongshuAccountManager,
        "fetch_personal_info",
        return_value={
            "success": True,
            "name": "用户A",
            "avatar": "http://avatar_a.png",
            "red_num": "111111",
            "fans_count": 10
        }
    ):
        mgr = XiaohongshuAccountManager(project_root=project_root, data_dir=data_dir)
        res = mgr.list_accounts()

        assert res["success"] is True
        assert len(res["accounts"]) == 1
        acc = res["accounts"][0]
        assert acc["username"] == "用户A"
        assert acc["red_num"] == "111111"
        assert acc["is_active"] is True
        assert mgr.accounts_file.exists()
        assert (mgr.accounts_dir / f"{acc['id']}.json").exists()


def test_switch_account(mock_env):
    project_root, data_dir = mock_env

    with patch.object(
        XiaohongshuAccountManager,
        "fetch_personal_info",
        return_value={"success": True, "name": "用户A", "red_num": "111", "avatar": ""}
    ):
        mgr = XiaohongshuAccountManager(project_root=project_root, data_dir=data_dir)

    # 手动添加第二个账号
    account_b_id = "acc_222"
    cookies_b = {
        "version": 2,
        "seed": 99999,
        "saved_at": "2026-11-20T00:00:00Z",
        "cookies": [
            {"name": "web_session", "value": "test_session_2", "domain": ".xiaohongshu.com"},
            {"name": "a1", "value": "test_a1_2", "domain": ".xiaohongshu.com"}
        ]
    }
    with open(mgr.accounts_dir / f"{account_b_id}.json", "w", encoding="utf-8") as f:
        json.dump(cookies_b, f)

    # 更新 accounts.json
    data = mgr._read_json_file(mgr.accounts_file)
    data["accounts"].append({
        "id": account_b_id,
        "username": "用户B",
        "red_num": "222",
        "avatar": "",
        "alias": "测试副号",
        "is_active": False,
        "creator_authorized": True,
        "status": "valid"
    })
    mgr._write_json_file(mgr.accounts_file, data)

    # 切换至账号 B
    with patch.object(
        XiaohongshuAccountManager,
        "fetch_personal_info",
        return_value={"success": True, "name": "用户B", "red_num": "222", "avatar": ""}
    ):
        switch_res = mgr.switch_account(account_b_id)
        assert switch_res["success"] is True
        assert switch_res["active_account"]["id"] == account_b_id
        assert switch_res["active_account"]["username"] == "用户B"

        # 检查 cookies.json 是否已写为账号 B 的内容
        curr_cookies = mgr.read_active_cookies()
        session_val = next(c["value"] for c in curr_cookies["cookies"] if c["name"] == "web_session")
        assert session_val == "test_session_2"

        # 检查账号列表
        accounts_res = mgr.list_accounts()
        acc_a = next(a for a in accounts_res["accounts"] if a["red_num"] == "111")
        acc_b = next(a for a in accounts_res["accounts"] if a["red_num"] == "222")
        assert acc_a["is_active"] is False
        assert acc_b["is_active"] is True

        # 切换回账号 A
        switch_back = mgr.switch_account(acc_a["id"])
        assert switch_back["success"] is True
        curr_cookies = mgr.read_active_cookies()
        session_val = next(c["value"] for c in curr_cookies["cookies"] if c["name"] == "web_session")
        assert session_val == "test_session_1"


def test_import_cookies(mock_env):
    project_root, data_dir = mock_env

    with patch.object(
        XiaohongshuAccountManager,
        "fetch_personal_info",
        return_value={"success": True, "name": "初始号", "red_num": "000"}
    ):
        mgr = XiaohongshuAccountManager(project_root=project_root, data_dir=data_dir)

    raw_header = "web_session=imported_sess_3; a1=imported_a1_3; sec_poison_id=abc"

    with patch.object(
        XiaohongshuAccountManager,
        "fetch_personal_info",
        return_value={"success": True, "name": "导入用户C", "red_num": "333333", "avatar": "http://c.png"}
    ):
        import_res = mgr.import_cookies(raw_header, alias="生活号")
        assert import_res["success"] is True
        assert import_res["account"]["username"] == "导入用户C"
        assert import_res["account"]["alias"] == "生活号"
        assert import_res["account"]["is_active"] is True

        # 检查当前活跃凭据已更新
        curr_cookies = mgr.read_active_cookies()
        session_val = next(c["value"] for c in curr_cookies["cookies"] if c["name"] == "web_session")
        assert session_val == "imported_sess_3"


def test_delete_account(mock_env):
    project_root, data_dir = mock_env

    with patch.object(
        XiaohongshuAccountManager,
        "fetch_personal_info",
        return_value={"success": True, "name": "账号1", "red_num": "111"}
    ):
        mgr = XiaohongshuAccountManager(project_root=project_root, data_dir=data_dir)

    # 导入账号2
    with patch.object(
        XiaohongshuAccountManager,
        "fetch_personal_info",
        return_value={"success": True, "name": "账号2", "red_num": "222"}
    ):
        mgr.import_cookies("web_session=sess2; a1=a1_2")

    acc_list = mgr.list_accounts()["accounts"]
    assert len(acc_list) == 2

    # 删除活跃账号（账号2），应自动回退到账号1
    active_acc = mgr.get_active_account()
    del_res = mgr.delete_account(active_acc["id"])
    assert del_res["success"] is True
    assert len(del_res["accounts"]) == 1
    assert mgr.get_active_account()["username"] == "账号1"


def test_publish_account_routes(monkeypatch):
    from flask import Flask
    from backend.routes.publish_routes import create_publish_blueprint

    app = Flask(__name__)
    app.register_blueprint(create_publish_blueprint(), url_prefix="/api")
    client = app.test_client()

    # 测试 GET /api/publish/accounts
    res = client.get("/api/publish/accounts")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "accounts" in data


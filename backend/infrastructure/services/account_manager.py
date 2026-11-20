"""
小红书多账号管理服务

负责多账号凭证的存储、切换、导入、扫码新增与状态检测。
确保各账号会话隔离，切换时不会删除或覆盖历史登录信息。
"""

from __future__ import annotations

import json
import logging
import os
import random
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

import requests

from backend.utils.mcp_manager import mcp_manager

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class XiaohongshuAccountManager:
    """小红书多账号管理器"""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        data_dir: Optional[Path] = None,
    ):
        self.project_root = project_root or Path(
            os.getenv("REDINK_ROOT") or Path(__file__).resolve().parents[3]
        )
        if data_dir:
            self.data_dir = data_dir
        else:
            data_root = (
                Path(os.getenv("REDINK_DATA_DIR"))
                if os.getenv("REDINK_DATA_DIR")
                else self.project_root / "data"
            )
            self.data_dir = data_root / "xiaohongshu"

        self.accounts_dir = self.data_dir / "accounts"
        self.accounts_file = self.data_dir / "accounts.json"
        self.root_cookies_file = self.project_root / "cookies.json"
        self.data_cookies_file = self.data_dir / "cookies.json"
        self.backup_cookies_file = self.data_dir / "cookies_backup_adding.json"

        self.accounts_dir.mkdir(parents=True, exist_ok=True)
        self.ensure_initialized()

    # ---------------- 基础辅助方法 ----------------

    def _read_json_file(self, path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else None
        except Exception as e:
            logger.warning(f"读取 JSON 文件失败 ({path}): {e}")
            return None

    def _write_json_file(self, path: Path, data: Dict[str, Any]) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"写入 JSON 文件失败 ({path}): {e}")
            return False

    def _extract_cookie_map(self, cookies: List[Dict[str, Any]]) -> Dict[str, str]:
        cookie_map: Dict[str, str] = {}
        for c in cookies:
            if isinstance(c, dict) and c.get("name") and c.get("value") is not None:
                cookie_map[str(c["name"])] = str(c["value"])
        return cookie_map

    def fetch_personal_info(self, cookie_map: Dict[str, str]) -> Dict[str, Any]:
        """请求小红书创作者接口获取个人信息与主页资料"""
        try:
            headers = {"User-Agent": USER_AGENT}
            resp = requests.get(
                "https://creator.xiaohongshu.com/api/galaxy/creator/home/personal_info",
                cookies=cookie_map,
                headers=headers,
                timeout=5,
            )
            if resp.status_code == 200:
                res_data = resp.json()
                if res_data.get("success") and res_data.get("code") == 0:
                    info = res_data.get("data") or {}
                    return {
                        "success": True,
                        "name": info.get("name") or "小红书创作者",
                        "avatar": info.get("avatar") or "",
                        "red_num": str(info.get("red_num") or ""),
                        "fans_count": info.get("fans_count", 0),
                        "personal_desc": info.get("personal_desc") or "",
                        "raw": info,
                    }
                else:
                    return {
                        "success": False,
                        "error": res_data.get("msg") or "创作者中心返回错误",
                        "code": res_data.get("code"),
                    }
            return {
                "success": False,
                "error": f"HTTP {resp.status_code}",
            }
        except Exception as e:
            logger.debug(f"请求创作者个人资料失败或离线: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _sync_galaxy_creator_cookie(self, cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """确保 galaxy_creator_session_id Cookie 注入同步"""
        if not isinstance(cookies, list) or not cookies:
            return cookies

        web_session = next(
            (
                c.get("value")
                for c in cookies
                if isinstance(c, dict)
                and c.get("name") == "web_session"
                and c.get("value")
            ),
            None,
        )
        if not web_session:
            return cookies

        # 清除已有的 galaxy_creator_session_id
        new_cookies = [
            c
            for c in cookies
            if not (isinstance(c, dict) and c.get("name") == "galaxy_creator_session_id")
        ]

        # 注入两项（根域与创作者子域）
        new_cookies.append(
            {
                "name": "galaxy_creator_session_id",
                "value": web_session,
                "domain": ".xiaohongshu.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "session": True,
            }
        )
        new_cookies.append(
            {
                "name": "galaxy_creator_session_id",
                "value": web_session,
                "domain": "creator.xiaohongshu.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "session": True,
            }
        )
        return new_cookies

    def write_active_cookies(self, cookie_data: Dict[str, Any]) -> bool:
        """
        将指定 Cookie 数据写入项目根目录 cookies.json 与 data/xiaohongshu/cookies.json，
        自动注入创作者凭证，保持双路径实时一致。
        """
        cookies = cookie_data.get("cookies", [])
        if isinstance(cookies, list):
            cookie_data["cookies"] = self._sync_galaxy_creator_cookie(cookies)

        ok1 = self._write_json_file(self.data_cookies_file, cookie_data)
        ok2 = self._write_json_file(self.root_cookies_file, cookie_data)
        return ok1 and ok2

    def read_active_cookies(self) -> Optional[Dict[str, Any]]:
        """从本地读取当前活跃 Cookie"""
        if self.data_cookies_file.exists():
            return self._read_json_file(self.data_cookies_file)
        if self.root_cookies_file.exists():
            return self._read_json_file(self.root_cookies_file)
        return None

    # ---------------- 自动初始化与迁移 ----------------

    def ensure_initialized(self) -> None:
        """若尚未建立 accounts.json，自动从现有 cookies.json 初始化迁移第一条账号数据"""
        if self.accounts_file.exists():
            return

        # 寻找现有的有效 Cookie
        existing_data = self.read_active_cookies()
        if not existing_data or not isinstance(existing_data.get("cookies"), list):
            return

        cookies = existing_data.get("cookies", [])
        cookie_map = self._extract_cookie_map(cookies)
        if "web_session" not in cookie_map and "a1" not in cookie_map:
            return

        # 探测账号信息
        profile = self.fetch_personal_info(cookie_map)
        username = profile.get("name") if profile.get("success") else "默认账号"
        red_num = profile.get("red_num") if profile.get("success") else ""
        avatar = profile.get("avatar") if profile.get("success") else ""

        account_id = f"acc_{red_num}" if red_num else f"acc_{int(time.time())}"
        account_file = self.accounts_dir / f"{account_id}.json"

        # 保存该账号的独立凭证
        self._write_json_file(account_file, existing_data)

        # 构建注册表
        now = _utcnow_iso()
        reg_data = {
            "active_account_id": account_id,
            "accounts": [
                {
                    "id": account_id,
                    "username": username,
                    "red_num": red_num,
                    "avatar": avatar,
                    "alias": "主账号",
                    "is_active": True,
                    "creator_authorized": profile.get("success", False),
                    "status": "valid" if profile.get("success") else "unknown",
                    "created_at": now,
                    "updated_at": now,
                    "last_used_at": now,
                }
            ],
        }
        self._write_json_file(self.accounts_file, reg_data)
        logger.info(f"已自动从现有 cookies.json 迁移初始账号: {username} ({account_id})")

    # ---------------- 账号查询与管理 ----------------

    def list_accounts(self) -> Dict[str, Any]:
        """获取所有账号列表及当前活跃账号 ID"""
        self.ensure_initialized()
        data = self._read_json_file(self.accounts_file)
        if not data or not isinstance(data.get("accounts"), list):
            return {
                "success": True,
                "accounts": [],
                "active_account_id": None,
                "active_account": None,
            }

        accounts = data.get("accounts", [])
        active_id = data.get("active_account_id")

        active_account = next((a for a in accounts if a.get("id") == active_id), None)
        if not active_account and accounts:
            active_account = accounts[0]
            active_id = active_account.get("id")

        # 确保各个账号 is_active 标识准确
        for a in accounts:
            a["is_active"] = (a.get("id") == active_id)

        return {
            "success": True,
            "accounts": accounts,
            "active_account_id": active_id,
            "active_account": active_account,
        }

    def get_active_account(self) -> Optional[Dict[str, Any]]:
        """获取当前活跃账号"""
        res = self.list_accounts()
        return res.get("active_account")

    def save_current_cookies_to_active_account(self) -> bool:
        """将当前活跃的 cookies.json 保存回当前活跃账号的凭证仓库"""
        active_account = self.get_active_account()
        if not active_account:
            return False

        account_id = active_account.get("id")
        current_cookies = self.read_active_cookies()
        if not current_cookies or not current_cookies.get("cookies"):
            return False

        account_file = self.accounts_dir / f"{account_id}.json"
        return self._write_json_file(account_file, current_cookies)

    def switch_account(self, account_id: str) -> Dict[str, Any]:
        """
        切换当前发布的账号：
        1. 保存当前活跃账号的最新 Cookie。
        2. 读取目标账号的独立 Cookie 并同步写入 cookies.json。
        3. 重启/重置 MCP 服务，保证浏览器进程与会话完全切换。
        4. 更新 accounts.json 活跃指向。
        5. 探测并返回目标账号最新状态。
        """
        self.ensure_initialized()
        data = self._read_json_file(self.accounts_file) or {"accounts": []}
        accounts: List[Dict[str, Any]] = data.get("accounts", [])

        target = next((a for a in accounts if a.get("id") == account_id), None)
        if not target:
            return {"success": False, "error": f"账号不存在: {account_id}"}

        # 1. 尝试备份当前账号
        self.save_current_cookies_to_active_account()

        # 2. 读取目标账号凭据
        target_file = self.accounts_dir / f"{account_id}.json"
        if not target_file.exists():
            return {
                "success": False,
                "error": f"账号凭据文件缺失，请重新登录此账号 ({account_id})",
            }

        target_cookies = self._read_json_file(target_file)
        if not target_cookies or not target_cookies.get("cookies"):
            return {
                "success": False,
                "error": "账号凭据为空或已损坏，请重新登录",
            }

        # 写入双路径
        self.write_active_cookies(target_cookies)

        # 3. 更新 accounts.json
        now = _utcnow_iso()
        data["active_account_id"] = account_id
        for a in accounts:
            a["is_active"] = (a.get("id") == account_id)
            if a.get("id") == account_id:
                a["last_used_at"] = now
                a["updated_at"] = now
        self._write_json_file(self.accounts_file, data)

        # 4. 重启 MCP 以重置浏览器上下文
        if mcp_manager.is_running():
            logger.info("切换账号：正在重启 MCP 服务以加载全新浏览器上下文...")
            try:
                mcp_manager.restart()
            except Exception as e:
                logger.warning(f"切换账号时重启 MCP 失败: {e}")

        # 5. 探活与状态刷新
        cookie_map = self._extract_cookie_map(target_cookies.get("cookies", []))
        profile = self.fetch_personal_info(cookie_map)
        if profile.get("success"):
            target["username"] = profile.get("name") or target.get("username")
            target["avatar"] = profile.get("avatar") or target.get("avatar")
            target["red_num"] = profile.get("red_num") or target.get("red_num")
            target["creator_authorized"] = True
            target["status"] = "valid"
            self._write_json_file(self.accounts_file, data)

        logger.info(f"成功切换至账号: {target.get('username')} ({account_id})")
        return {
            "success": True,
            "message": f"已切换至账号：{target.get('username')}",
            "active_account": target,
        }

    # ---------------- 扫码添加新账号 ----------------

    async def start_add_account(self) -> Dict[str, Any]:
        """
        开始扫码添加新账号流程：
        1. 备份当前活跃账号凭证。
        2. 写入临时空 Cookie 文件，并重启/重置 MCP 使其呈现未登录状态。
        3. 调用 MCP 的 get_login_qrcode 获取全新登录二维码。
        """
        self.ensure_initialized()

        # 1. 备份当前活跃凭证
        self.save_current_cookies_to_active_account()
        current = self.read_active_cookies()
        if current:
            self._write_json_file(self.backup_cookies_file, current)

        # 2. 写入空凭据
        empty_cookies = {
            "version": 2,
            "seed": random.randint(1000000000, 2147483647),
            "saved_at": _utcnow_iso(),
            "cookies": [],
        }
        self.write_active_cookies(empty_cookies)

        # 3. 确保 MCP 重启以释放上一个账号会话
        if mcp_manager.is_running():
            mcp_manager.restart()
        else:
            mcp_manager.ensure_running()

        # 4. 请求登录二维码
        try:
            result = await mcp_manager.call_tool("get_login_qrcode")
            # 兼容 structuredContent 或直接返回
            qrcode = result.get("qrcode")
            if not qrcode and isinstance(result.get("image"), dict):
                qrcode = result["image"].get("data_url")

            if not qrcode:
                error_msg = str(result.get("error") or result.get("message") or "获取登录二维码失败")
                return {"success": False, "error": error_msg}

            return {
                "success": True,
                "qrcode": qrcode,
                "timeout": result.get("timeout", 300),
                "message": result.get("message") or "请使用手机小红书 App 扫描二维码添加账号",
            }
        except Exception as e:
            logger.error(f"获取登录二维码异常: {e}")
            return {"success": False, "error": str(e)}

    def check_add_status(self) -> Dict[str, Any]:
        """
        检查新账号登录是否已完成：
        检查本地 cookies.json 是否已成功写入 web_session 或 a1。
        若就绪，立即拉取创作者信息并持久化为新账号。
        """
        current_data = self.read_active_cookies()
        if not current_data or not current_data.get("cookies"):
            return {
                "success": True,
                "logged_in": False,
                "message": "等待扫码中...",
            }

        cookies = current_data.get("cookies", [])
        cookie_map = self._extract_cookie_map(cookies)
        if "web_session" not in cookie_map and "a1" not in cookie_map:
            return {
                "success": True,
                "logged_in": False,
                "message": "等待扫码中...",
            }

        # 探测新账号个人信息
        profile = self.fetch_personal_info(cookie_map)
        username = profile.get("name") if profile.get("success") else "新账号"
        red_num = profile.get("red_num") if profile.get("success") else ""
        avatar = profile.get("avatar") if profile.get("success") else ""

        # 生成账号 ID
        account_id = f"acc_{red_num}" if red_num else f"acc_{int(time.time())}"

        # 存入独立账号文件
        account_file = self.accounts_dir / f"{account_id}.json"
        self._write_json_file(account_file, current_data)

        # 更新注册表
        data = self._read_json_file(self.accounts_file) or {"accounts": []}
        accounts: List[Dict[str, Any]] = data.get("accounts", [])

        existing = next((a for a in accounts if a.get("id") == account_id), None)
        now = _utcnow_iso()
        if existing:
            # 重新登录已有账号，更新凭证
            existing["username"] = username
            existing["avatar"] = avatar
            existing["red_num"] = red_num
            existing["creator_authorized"] = profile.get("success", False)
            existing["status"] = "valid"
            existing["updated_at"] = now
            existing["last_used_at"] = now
            account_record = existing
        else:
            account_record = {
                "id": account_id,
                "username": username,
                "red_num": red_num,
                "avatar": avatar,
                "alias": f"账号 {len(accounts) + 1}",
                "is_active": True,
                "creator_authorized": profile.get("success", False),
                "status": "valid",
                "created_at": now,
                "updated_at": now,
                "last_used_at": now,
            }
            accounts.append(account_record)

        data["active_account_id"] = account_id
        for a in accounts:
            a["is_active"] = (a.get("id") == account_id)
        self._write_json_file(self.accounts_file, data)

        # 自动同步创作者 session 并写回
        self.write_active_cookies(current_data)

        # 清除备份
        if self.backup_cookies_file.exists():
            try:
                self.backup_cookies_file.unlink()
            except Exception:
                pass

        logger.info(f"成功添加并激活新账号: {username} ({account_id})")
        return {
            "success": True,
            "logged_in": True,
            "account": account_record,
            "message": f"成功添加账号：{username}",
        }

    def cancel_add_account(self) -> Dict[str, Any]:
        """取消扫码添加账号，恢复原活跃账号凭证"""
        if self.backup_cookies_file.exists():
            backup_data = self._read_json_file(self.backup_cookies_file)
            if backup_data:
                self.write_active_cookies(backup_data)
            try:
                self.backup_cookies_file.unlink()
            except Exception:
                pass

            if mcp_manager.is_running():
                mcp_manager.restart()

        active = self.get_active_account()
        return {
            "success": True,
            "message": "已取消添加新账号，恢复原账号状态",
            "active_account": active,
        }

    # ---------------- Cookie 直接导入 ----------------

    def import_cookies(self, cookie_input: str, alias: Optional[str] = None) -> Dict[str, Any]:
        """
        直接导入 Cookie 添加账号：
        支持 JSON 格式（如 EditThisCookie 导出）或 header 字符串（a=1; b=2）。
        校验有效性后自动持久化并设为当前活跃账号。
        """
        raw = (cookie_input or "").strip()
        if not raw:
            return {"success": False, "error": "Cookie 输入内容不能为空"}

        cookies_list: List[Dict[str, Any]] = []

        # 尝试作为 JSON 解析
        if raw.startswith("{") or raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    cookies_list = parsed
                elif isinstance(parsed, dict):
                    if isinstance(parsed.get("cookies"), list):
                        cookies_list = parsed["cookies"]
                    else:
                        cookies_list = [
                            {"name": k, "value": v, "domain": ".xiaohongshu.com", "path": "/"}
                            for k, v in parsed.items()
                        ]
            except Exception as e:
                return {"success": False, "error": f"JSON 解析失败: {e}"}
        else:
            # 尝试作为 Header key=val; 字符串解析
            pairs = raw.split(";")
            for p in pairs:
                p = p.strip()
                if not p or "=" not in p:
                    continue
                k, v = p.split("=", 1)
                cookies_list.append({
                    "name": k.strip(),
                    "value": v.strip(),
                    "domain": ".xiaohongshu.com",
                    "path": "/",
                })

        if not cookies_list:
            return {"success": False, "error": "未解析出任何有效的 Cookie 项"}

        cookie_map = self._extract_cookie_map(cookies_list)
        if "web_session" not in cookie_map and "a1" not in cookie_map:
            return {
                "success": False,
                "error": "Cookie 中缺少 web_session 或 a1 关键字段，无法维持小红书登录态",
            }

        # 验证该 Cookie 是否真实有效
        profile = self.fetch_personal_info(cookie_map)
        if not profile.get("success"):
            return {
                "success": False,
                "error": f"Cookie 验证失败（无法访问创作者服务中心）: {profile.get('error', '凭证已失效')}",
            }

        username = profile.get("name") or "导入账号"
        red_num = profile.get("red_num") or ""
        avatar = profile.get("avatar") or ""

        account_id = f"acc_{red_num}" if red_num else f"acc_{int(time.time())}"
        now = _utcnow_iso()

        full_payload = {
            "version": 2,
            "seed": random.randint(1000000000, 2147483647),
            "saved_at": now,
            "cookies": self._sync_galaxy_creator_cookie(cookies_list),
        }

        # 保存凭证
        account_file = self.accounts_dir / f"{account_id}.json"
        self._write_json_file(account_file, full_payload)

        # 更新注册表
        data = self._read_json_file(self.accounts_file) or {"accounts": []}
        accounts: List[Dict[str, Any]] = data.get("accounts", [])

        existing = next((a for a in accounts if a.get("id") == account_id), None)
        if existing:
            existing["username"] = username
            existing["avatar"] = avatar
            existing["red_num"] = red_num
            if alias:
                existing["alias"] = alias
            existing["creator_authorized"] = True
            existing["status"] = "valid"
            existing["updated_at"] = now
            existing["last_used_at"] = now
            account_record = existing
        else:
            account_record = {
                "id": account_id,
                "username": username,
                "red_num": red_num,
                "avatar": avatar,
                "alias": alias or f"账号 {len(accounts) + 1}",
                "is_active": True,
                "creator_authorized": True,
                "status": "valid",
                "created_at": now,
                "updated_at": now,
                "last_used_at": now,
            }
            accounts.append(account_record)

        data["active_account_id"] = account_id
        for a in accounts:
            a["is_active"] = (a.get("id") == account_id)
        self._write_json_file(self.accounts_file, data)

        # 写入活跃并重启 MCP
        self.write_active_cookies(full_payload)
        if mcp_manager.is_running():
            mcp_manager.restart()

        logger.info(f"成功导入并激活账号: {username} ({account_id})")
        return {
            "success": True,
            "account": account_record,
            "message": f"导入成功，已切换至账号：{username}",
        }

    # ---------------- 账号修改与删除 ----------------

    def update_account_alias(self, account_id: str, alias: str) -> Dict[str, Any]:
        """修改账号别名备注"""
        self.ensure_initialized()
        data = self._read_json_file(self.accounts_file) or {"accounts": []}
        accounts: List[Dict[str, Any]] = data.get("accounts", [])

        target = next((a for a in accounts if a.get("id") == account_id), None)
        if not target:
            return {"success": False, "error": f"账号不存在: {account_id}"}

        target["alias"] = str(alias or "").strip()
        target["updated_at"] = _utcnow_iso()
        self._write_json_file(self.accounts_file, data)
        return {"success": True, "account": target}

    def delete_account(self, account_id: str) -> Dict[str, Any]:
        """
        删除指定账号：
        1. 从 accounts.json 移除。
        2. 删除对应独立凭据 json 文件。
        3. 若删除的是当前活跃账号，自动切换到剩余的第一个账号；若无剩余则清空。
        """
        self.ensure_initialized()
        data = self._read_json_file(self.accounts_file) or {"accounts": []}
        accounts: List[Dict[str, Any]] = data.get("accounts", [])

        target = next((a for a in accounts if a.get("id") == account_id), None)
        if not target:
            return {"success": False, "error": f"账号不存在: {account_id}"}

        accounts.remove(target)

        # 删除凭据文件
        account_file = self.accounts_dir / f"{account_id}.json"
        if account_file.exists():
            try:
                account_file.unlink()
            except Exception as e:
                logger.warning(f"删除账号凭据文件失败: {e}")

        # 如果删除的是活跃账号
        was_active = (data.get("active_account_id") == account_id)
        new_active_account = None

        if was_active:
            if accounts:
                next_acc = accounts[0]
                data["active_account_id"] = next_acc.get("id")
                # 切换至下一个
                next_file = self.accounts_dir / f"{next_acc.get('id')}.json"
                if next_file.exists():
                    next_cookies = self._read_json_file(next_file)
                    if next_cookies:
                        self.write_active_cookies(next_cookies)
                new_active_account = next_acc
            else:
                data["active_account_id"] = None
                # 清空本地 cookies.json
                empty = {"version": 2, "cookies": []}
                self.write_active_cookies(empty)

            if mcp_manager.is_running():
                mcp_manager.restart()

        for a in accounts:
            a["is_active"] = (a.get("id") == data.get("active_account_id"))

        self._write_json_file(self.accounts_file, data)
        logger.info(f"已删除账号: {target.get('username')} ({account_id})")

        return {
            "success": True,
            "message": f"已删除账号：{target.get('username')}",
            "accounts": accounts,
            "active_account": new_active_account,
        }

    def refresh_account_status(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        主动刷新账号状态与创作者授权：
        默认刷新当前活跃账号；亦可刷新指定账号。
        """
        self.ensure_initialized()
        data = self._read_json_file(self.accounts_file) or {"accounts": []}
        accounts: List[Dict[str, Any]] = data.get("accounts", [])

        target_id = account_id or data.get("active_account_id")
        target = next((a for a in accounts if a.get("id") == target_id), None)
        if not target:
            return {"success": False, "error": "未找到需要刷新的账号"}

        # 读取该账号凭证
        account_file = self.accounts_dir / f"{target_id}.json"
        cookies_data = self._read_json_file(account_file) if account_file.exists() else None
        if not cookies_data:
            cookies_data = self.read_active_cookies()

        if not cookies_data or not cookies_data.get("cookies"):
            target["status"] = "expired"
            target["creator_authorized"] = False
            self._write_json_file(self.accounts_file, data)
            return {
                "success": False,
                "account": target,
                "error": "账号凭据不存在或已失效",
            }

        cookie_map = self._extract_cookie_map(cookies_data.get("cookies", []))
        profile = self.fetch_personal_info(cookie_map)
        now = _utcnow_iso()
        target["updated_at"] = now

        if profile.get("success"):
            target["username"] = profile.get("name") or target.get("username")
            target["avatar"] = profile.get("avatar") or target.get("avatar")
            target["red_num"] = profile.get("red_num") or target.get("red_num")
            target["creator_authorized"] = True
            target["status"] = "valid"
        else:
            target["creator_authorized"] = False
            target["status"] = "expired"

        self._write_json_file(self.accounts_file, data)

        # 若刷新的是活跃账号，更新本地 cookies 文件
        if target.get("id") == data.get("active_account_id"):
            self.write_active_cookies(cookies_data)

        return {
            "success": True,
            "account": target,
            "message": f"账号状态已更新（{target.get('username')}）",
        }


# 全局单例
account_manager = XiaohongshuAccountManager()

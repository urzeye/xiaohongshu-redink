"""
小红书发布服务

使用 xiaohongshu-mcp 提供的工具进行发布操作。
"""

import json
import logging
import os
import re
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import unquote, urlparse

from backend.domain.ports import PublishGatewayPort
from backend.infrastructure.gateways import get_publish_gateway

logger = logging.getLogger(__name__)


class PublishService:
    """
    小红书发布服务

    封装 xiaohongshu-mcp 的发布相关功能，提供统一的接口。
    """

    def __init__(self, gateway: PublishGatewayPort | None = None):
        self.gateway = gateway or get_publish_gateway()
        self.project_root = Path(os.getenv("REDINK_ROOT") or Path(__file__).resolve().parents[3])
        data_dir_env = os.getenv("REDINK_DATA_DIR")
        self.history_root_dir = Path(data_dir_env) / "history" if data_dir_env else self.project_root / "history"

    @staticmethod
    def _path_exists(path: str) -> bool:
        try:
            return bool(path) and Path(path).exists()
        except Exception:
            return False

    @staticmethod
    def _extract_api_image_ref(path: str) -> Optional[tuple[str, str]]:
        normalized = (path or "").strip().lstrip("/")
        parts = normalized.split("/")
        if len(parts) < 4:
            return None
        if parts[0] != "api" or parts[1] != "images":
            return None
        task_id = unquote(parts[2]).strip()
        filename = unquote(parts[3]).strip()
        if not task_id or not filename:
            return None
        return task_id, filename

    def _resolve_publish_image_path(self, image: Any) -> str:
        raw = unquote(str(image or "").strip())
        if not raw:
            return ""

        parsed = urlparse(raw)
        api_ref = self._extract_api_image_ref(parsed.path if parsed.path else raw)
        if api_ref:
            task_id, filename = api_ref
            image_path = self.history_root_dir / task_id / filename
            if image_path.exists():
                return str(image_path)

            # 若前端传入缩略图名，优先回退到原图。
            if filename.startswith("thumb_"):
                original_path = self.history_root_dir / task_id / filename[len("thumb_"):]
                if original_path.exists():
                    return str(original_path)
            else:
                # 原图缺失时兜底缩略图，避免直接失败。
                thumb_path = self.history_root_dir / task_id / f"thumb_{filename}"
                if thumb_path.exists():
                    logger.warning(f"发布原图缺失，回退缩略图: {raw}")
                    return str(thumb_path)

            # 兼容回退：尝试从项目根目录历史文件夹查找
            proj_history = self.project_root / "history"
            if proj_history != self.history_root_dir:
                proj_image = proj_history / task_id / filename
                if proj_image.exists():
                    return str(proj_image)
                if filename.startswith("thumb_"):
                    proj_orig = proj_history / task_id / filename[len("thumb_"):]
                    if proj_orig.exists():
                        return str(proj_orig)
                else:
                    proj_thumb = proj_history / task_id / f"thumb_{filename}"
                    if proj_thumb.exists():
                        return str(proj_thumb)

            return str(image_path)

        # 已是本地绝对路径时直接透传。
        if os.path.isabs(raw) or re.match(r"^[A-Za-z]:[\\/]", raw):
            return raw

        # 相对路径尝试按项目根目录解析。
        project_path = (self.project_root / raw).resolve()
        if project_path.exists():
            return str(project_path)
        return raw

    def _normalize_publish_images(self, images: List[str]) -> tuple[List[str], List[str]]:
        resolved: List[str] = []
        missing: List[str] = []
        for index, image in enumerate(images):
            normalized = self._resolve_publish_image_path(image)
            resolved.append(normalized)
            if not self._path_exists(normalized):
                missing.append(f"[{index}] {image} -> {normalized}")
        return resolved, missing

    @staticmethod
    def _extract_first_url(text: str) -> Optional[str]:
        if not isinstance(text, str) or not text.strip():
            return None
        matches = re.findall(r"https?://[^\s\"'<>）)]+", text)
        if not matches:
            return None

        # 优先返回小红书相关链接。
        for candidate in matches:
            lowered = candidate.lower()
            if "xiaohongshu.com" in lowered or "xhslink.com" in lowered:
                return candidate
        return matches[0]

    def _extract_post_url(self, result: Dict[str, Any]) -> Optional[str]:
        def _pick_url(value: Any) -> Optional[str]:
            if isinstance(value, str):
                candidate = value.strip()
                if candidate.startswith("http://") or candidate.startswith("https://"):
                    return candidate
                return self._extract_first_url(candidate)
            if isinstance(value, dict):
                return self._extract_post_url(value)
            return None

        key_candidates = (
            "post_url",
            "postUrl",
            "url",
            "note_url",
            "noteUrl",
            "publish_url",
            "publishUrl",
            "post_link",
            "link",
        )
        for key in key_candidates:
            if key in result:
                found = _pick_url(result.get(key))
                if found:
                    return found

        for key in ("message", "result", "content", "data"):
            if key in result:
                found = _pick_url(result.get(key))
                if found:
                    return found

        return None

    @staticmethod
    def _coerce_bool(value: Any) -> Optional[bool]:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "y", "ok", "logged_in", "loggedin", "已登录"}:
                return True
            if lowered in {"0", "false", "no", "n", "not_logged_in", "未登录"}:
                return False
        return None

    def _extract_logged_in(self, result: Dict[str, Any], message: str) -> bool:
        for key in (
            "logged_in",
            "is_logged_in",
            "isLogin",
            "is_login",
            "login",
            "loggedIn",
            "isLoggedIn",
            "has_login",
        ):
            if key in result:
                parsed = self._coerce_bool(result.get(key))
                if parsed is not None:
                    return parsed

        lowered = message.lower()
        negative_signals = (
            "未登录",
            "需要登录",
            "请先登录",
            "not logged in",
            "login required",
            "login first",
        )
        positive_signals = (
            "已登录",
            "登录成功",
            "logged in",
            "login success",
            "you are logged in",
        )
        if any(signal in lowered for signal in negative_signals):
            return False
        if any(signal in lowered for signal in positive_signals):
            return True
        return False

    @staticmethod
    def _extract_username(result: Dict[str, Any], message: str) -> Optional[str]:
        direct_username = result.get("username")
        if isinstance(direct_username, str) and direct_username.strip():
            return direct_username.strip()

        user_info = result.get("user_info")
        if isinstance(user_info, dict):
            for key in ("username", "user_name", "nickname", "nick_name"):
                value = user_info.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        match = re.search(r"(?:用户名|账号|username)\s*[：:]\s*([^\s,，。;；]+)", message, flags=re.IGNORECASE)
        if match:
            username = match.group(1).strip()
            return username or None
        return None

    async def get_mcp_status(self) -> Dict[str, Any]:
        """
        获取 MCP 服务状态

        Returns:
            dict: 包含 running, url, binary_installed 等信息
        """
        return self.gateway.get_status()

    async def start_service(self) -> Dict[str, Any]:
        """
        启动 MCP / VibeSurf 服务进程

        Returns:
            dict: 启动结果与当前状态
        """
        if hasattr(self.gateway, "start_service"):
            result = self.gateway.start_service()
            if isinstance(result, dict):
                return result
            return {"success": bool(result), "running": bool(result)}
        status = await self.get_mcp_status()
        return {"success": status.get("running", False), **status}

    async def install_mcp_binary(self) -> Dict[str, Any]:
        """
        安装 xiaohongshu-mcp 二进制。

        Returns:
            dict: 安装结果
        """
        return self.gateway.install_binary()

    def _sync_creator_session_cookie(self) -> bool:
        """
        自动同步 galaxy_creator_session_id 到 cookies.json。

        背景：新版小红书创作者服务平台已与主站会话（web_session）深度融合，
        不再单独下发 galaxy_creator_session_id Cookie；但底层 xiaohongshu-mcp
        二进制的 hasCreatorSession() 仍硬编码校验此 Cookie。
        若缺失，mcp 会误判为“创作者中心登录失效，请重新扫码登录”。

        此函数将当前主站 web_session 映射注入为 galaxy_creator_session_id，
        确保 MCP 检查通过并顺利进入发布流程。
        """
        cookies_file = self.project_root / "cookies.json"
        if not cookies_file.exists():
            return False
        try:
            with open(cookies_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            cookies = data.get("cookies", [])
            if not isinstance(cookies, list) or not cookies:
                return False

            web_session = next(
                (c.get("value") for c in cookies if isinstance(c, dict) and c.get("name") == "web_session" and c.get("value")),
                None
            )
            if not web_session:
                return False

            existing_galaxy = [
                c for c in cookies if isinstance(c, dict) and c.get("name") == "galaxy_creator_session_id"
            ]

            # 如果已经存在且值匹配，无需重复写入
            if existing_galaxy and any(c.get("value") == web_session for c in existing_galaxy):
                return True

            # 清理旧的 galaxy_creator_session_id 项
            cookies = [c for c in cookies if not (isinstance(c, dict) and c.get("name") == "galaxy_creator_session_id")]

            # 注入新的映射项（支持顶级域名和创作者子域）
            cookies.append({
                "name": "galaxy_creator_session_id",
                "value": web_session,
                "domain": ".xiaohongshu.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "session": True,
            })
            cookies.append({
                "name": "galaxy_creator_session_id",
                "value": web_session,
                "domain": "creator.xiaohongshu.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "session": True,
            })

            data["cookies"] = cookies
            with open(cookies_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("已自动同步 galaxy_creator_session_id 到 cookies.json")
            return True
        except Exception as e:
            logger.warning(f"自动同步创作者中心会话 Cookie 失败: {e}")
            return False

    def _get_local_cookies_status(self) -> Dict[str, Any]:
        """从本地 cookies.json 检查登录与创作者中心凭证状态"""
        # 优先确保创作者会话 Cookie 已同步
        self._sync_creator_session_cookie()

        cookies_file = self.project_root / "cookies.json"
        if not cookies_file.exists():
            return {
                "has_file": False,
                "logged_in": False,
                "creator_authorized": False,
                "username": None,
                "message": "未登录，请先登录小红书",
            }
        try:
            with open(cookies_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            cookies = data.get("cookies", [])
            if not isinstance(cookies, list) or len(cookies) == 0:
                return {
                    "has_file": True,
                    "logged_in": False,
                    "creator_authorized": False,
                    "username": None,
                    "message": "未登录，请先登录小红书",
                }

            cookie_map = {c.get("name"): c.get("value") for c in cookies if isinstance(c, dict) and c.get("name")}
            has_main_session = bool("web_session" in cookie_map or "a1" in cookie_map)

            if not has_main_session:
                return {
                    "has_file": True,
                    "logged_in": False,
                    "creator_authorized": False,
                    "username": None,
                    "message": "未登录，请先登录小红书",
                }

            # 探测创作者中心会话有效性（小红书顶级域名 Cookie 全域共享，优先请求创作者轻量接口验证）
            creator_username = None
            try:
                import requests
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
                }
                resp = requests.get(
                    "https://creator.xiaohongshu.com/api/galaxy/creator/home/personal_info",
                    cookies=cookie_map,
                    headers=headers,
                    timeout=3
                )
                if resp.status_code == 200:
                    res_data = resp.json()
                    if res_data.get("success") and res_data.get("code") == 0:
                        creator_username = res_data.get("data", {}).get("name")
            except Exception as e:
                logger.debug(f"探测创作者个人信息失败或离线: {e}")

            return {
                "has_file": True,
                "logged_in": True,
                "creator_authorized": True,
                "username": creator_username,
                "message": f"小红书及创作者中心已就绪（{creator_username}）" if creator_username else "小红书及创作者中心已就绪",
            }
        except Exception as e:
            logger.warning(f"读取本地 cookies.json 失败: {e}")
            return {
                "has_file": False,
                "logged_in": False,
                "creator_authorized": False,
                "username": None,
                "message": "检查登录状态失败",
            }

    async def check_login(self, force: bool = False) -> Dict[str, Any]:
        """
        检查小红书登录状态
        优先检查本地 cookies.json 避免无意义弹出浏览器。
        """
        if not force:
            local_status = self._get_local_cookies_status()
            if local_status.get("has_file") and local_status.get("logged_in"):
                return {
                    "success": True,
                    "logged_in": local_status["logged_in"],
                    "creator_authorized": local_status["creator_authorized"],
                    "username": local_status["username"],
                    "message": local_status["message"],
                }

        result = await self.gateway.check_login()

        if not result.get("success", True):
            return {
                "success": False,
                "logged_in": False,
                "creator_authorized": False,
                "message": result.get("error", "检查登录状态失败")
            }

        raw_message = str(result.get("message") or "").strip()
        logged_in = self._extract_logged_in(result, raw_message)
        username = self._extract_username(result, raw_message)
        user_info = result.get("user_info")
        if not isinstance(user_info, dict):
            user_info = {}
        if username and not user_info.get("username"):
            user_info["username"] = username

        local_status = self._get_local_cookies_status()
        creator_authorized = local_status.get("creator_authorized", False) if logged_in else False

        msg = raw_message
        if logged_in and not creator_authorized:
            msg = "小红书主站已登录，但创作者中心未授权（无法发布）"

        return {
            "success": True,
            "logged_in": logged_in,
            "creator_authorized": creator_authorized,
            "username": username,
            "message": msg or ("已登录" if logged_in else "未登录，请先登录小红书"),
            "user_info": user_info or None,
        }

    async def open_creator_login(self) -> Dict[str, Any]:
        """
        打开小红书创作者服务平台登录，获取创作者凭证
        """
        creator_url = "https://creator.xiaohongshu.com/login"
        try:
            logger.info(f"在系统浏览器中打开小红书创作者平台: {creator_url}")
            opened = webbrowser.open(creator_url)
            return {
                "success": True,
                "message": "已在浏览器中打开小红书创作者服务平台，登录或授权后点击【刷新状态】",
            }
        except Exception as e:
            logger.error(f"打开创作者中心登录失败: {e}")
            return {
                "success": False,
                "error": f"无法打开创作者登录页: {str(e)}",
            }

    async def open_login_page(self) -> Dict[str, Any]:
        """
        打开小红书登录页面

        Returns:
            dict: 操作结果
        """
        return await self.gateway.open_login_page()

    async def publish(
        self,
        title: str,
        content: str,
        images: List[str],
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        发布内容到小红书

        Args:
            title: 标题（最多20字）
            content: 正文内容
            images: 图片文件路径列表
            tags: 标签列表（可选）

        Returns:
            dict: {
                "success": bool,
                "message": str,
                "post_url": str (如果发布成功)
            }
        """
        # 校验标题长度
        if len(title) > 20:
            title = title[:20]
            logger.warning(f"标题超过20字，已截断: {title}")

        # 将标签添加到内容末尾
        full_content = content
        if tags and len(tags) > 0:
            tag_str = " ".join(f"#{tag}" for tag in tags[:5])  # 最多5个标签
            full_content = f"{content}\n\n{tag_str}"

        normalized_images, missing_images = self._normalize_publish_images(images)
        if missing_images:
            details = "; ".join(missing_images[:3])
            if len(missing_images) > 3:
                details += f"; ... 共 {len(missing_images)} 张"
            logger.error(f"发布失败：图片文件不可访问: {details}")
            return {
                "success": False,
                "message": "发布失败：图片文件不可访问，请刷新结果页后重试",
                "error": f"图片文件不存在或路径无效: {details}",
            }

        # 前置校验登录态，避免未登录时盲目调用发布报错
        local_status = self._get_local_cookies_status()
        if not local_status.get("creator_authorized") and not local_status.get("logged_in"):
            logger.warning("发布被拦截：未登录小红书")
            return {
                "success": False,
                "message": "小红书登录已失效，请先完成登录后再发布",
                "error": "小红书登录已失效，请先完成登录后再发布",
            }

        logger.info(f"开始发布到小红书: title={title}, images={len(images)}")

        # 调用 MCP 发布工具
        result = await self.gateway.publish({
            "title": title,
            "content": full_content,
            "images": normalized_images
        })

        if not result.get("success", True):
            err_msg = result.get("error") or result.get("message") or "发布失败"
            logger.error(f"发布失败: {err_msg}")
            return {
                "success": False,
                "message": err_msg,
                "error": err_msg,
            }

        logger.info("发布成功！")
        post_url = self._extract_post_url(result)
        return {
            "success": True,
            "message": "发布成功",
            "post_url": post_url
        }

    async def publish_with_video(
        self,
        title: str,
        content: str,
        video_path: str,
        cover_image: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        发布视频到小红书

        Args:
            title: 标题
            content: 正文
            video_path: 视频文件路径
            cover_image: 封面图片路径（可选）
            tags: 标签列表

        Returns:
            dict: 发布结果
        """
        full_content = content
        if tags and len(tags) > 0:
            tag_str = " ".join(f"#{tag}" for tag in tags[:5])
            full_content = f"{content}\n\n{tag_str}"

        result = await self.gateway.publish_video({
            "title": title[:20],
            "content": full_content,
            "video_path": video_path,
            "cover_image": cover_image
        })

        return result

    async def list_my_posts(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        获取我的帖子列表

        Args:
            page: 页码
            limit: 每页数量

        Returns:
            dict: 帖子列表
        """
        return await self.gateway.list_posts({"page": page, "limit": limit})

    async def search_posts(self, keyword: str, page: int = 1) -> Dict[str, Any]:
        """
        搜索帖子

        Args:
            keyword: 搜索关键词
            page: 页码

        Returns:
            dict: 搜索结果
        """
        return await self.gateway.search_posts({"keyword": keyword, "page": page})


# 全局服务实例
publish_service = PublishService()

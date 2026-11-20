"""
发布相关 API 路由

提供小红书发布功能的 REST API 接口。
"""

import logging
from flask import Blueprint, request

from backend.application.services import get_publish_application_service
from backend.interfaces.http import json_response

logger = logging.getLogger(__name__)
publish_application_service = get_publish_application_service()


def create_publish_blueprint():
    """创建发布路由蓝图"""
    publish_bp = Blueprint('publish', __name__)

    # ==================== MCP 状态 ====================

    @publish_bp.route('/publish/status', methods=['GET'])
    def get_mcp_status():
        """
        获取 MCP 服务状态

        返回：
        - running: MCP 服务是否运行
        - binary_installed: 二进制文件是否已安装
        - url: MCP 服务地址
        """
        try:
            status = publish_application_service.get_mcp_status()

            return json_response({
                "success": True,
                **status
            }, 200)
        except Exception as e:
            logger.error(f"获取 MCP 状态失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, 500)

    @publish_bp.route('/publish/start', methods=['POST'])
    def start_mcp_service():
        """
        启动 MCP / VibeSurf 服务进程
        """
        try:
            result = publish_application_service.start_service()
            status_code = 200 if result.get("success") or result.get("running") else 500
            return json_response(result, status_code)
        except Exception as e:
            logger.error(f"启动 MCP 服务失败: {e}")
            return json_response({
                "success": False,
                "running": False,
                "error": str(e)
            }, 500)

    @publish_bp.route('/publish/install-tools', methods=['POST'])
    def install_mcp_tools():
        """
        安装 xiaohongshu-mcp 工具链。

        返回：
        - success: 是否安装成功
        - message/error: 结果消息
        - status: 安装后 MCP 状态
        - output: 安装日志（截断）
        """
        try:
            result = publish_application_service.install_mcp_binary()
            if result.get("success"):
                status_code = 200
            elif result.get("code") == "install_in_progress":
                status_code = 409
            else:
                status_code = 500
            return json_response(result, status_code)
        except Exception as e:
            logger.error(f"安装 MCP 工具失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, 500)

    # ==================== 登录状态 ====================

    @publish_bp.route('/publish/login-check', methods=['GET'])
    def check_login():
        """
        检查小红书登录状态

        查询参数：
        - force: 是否强制调用 MCP 真实检测（默认 false 优先读本地凭证）

        返回：
        - logged_in: 是否已登录
        - creator_authorized: 是否已获得创作者服务中心授权
        - message: 状态消息
        - user_info: 用户信息（如果已登录）
        """
        try:
            force = request.args.get('force', 'false').lower() in ('true', '1')
            result = publish_application_service.check_login(force=force)

            return json_response(result, 200)
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return json_response({
                "success": False,
                "logged_in": False,
                "creator_authorized": False,
                "message": f"检查失败: {str(e)}",
                "error": str(e)
            }, 500)

    @publish_bp.route('/publish/login', methods=['POST'])
    def open_login():
        """
        打开小红书登录页面或获取扫码登录二维码
        """
        try:
            result = publish_application_service.open_login_page()

            return json_response(result, 200)
        except Exception as e:
            logger.error(f"打开登录页面失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, 500)

    @publish_bp.route('/publish/creator-login', methods=['POST'])
    def open_creator_login():
        """
        打开小红书创作者服务平台登录窗口/页面
        """
        try:
            result = publish_application_service.open_creator_login()
            return json_response(result, 200)
        except Exception as e:
            logger.error(f"打开创作者中心登录失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, 500)

    # ==================== 多账号管理 ====================

    @publish_bp.route('/publish/accounts', methods=['GET'])
    def list_accounts():
        """获取所有已保存的小红书账号列表"""
        try:
            result = publish_application_service.list_accounts()
            return json_response(result, 200)
        except Exception as e:
            logger.error(f"获取账号列表失败: {e}")
            return json_response({"success": False, "error": str(e)}, 500)

    @publish_bp.route('/publish/accounts/switch', methods=['POST'])
    def switch_account():
        """切换当前发布账号"""
        try:
            data = request.get_json(silent=True) or {}
            account_id = data.get("account_id")
            if not account_id:
                return json_response({"success": False, "error": "请提供目标账号 account_id"}, 400)
            result = publish_application_service.switch_account(account_id)
            status_code = 200 if result.get("success") else 400
            return json_response(result, status_code)
        except Exception as e:
            logger.error(f"切换账号失败: {e}")
            return json_response({"success": False, "error": str(e)}, 500)

    @publish_bp.route('/publish/accounts/start-add', methods=['POST'])
    def start_add_account():
        """开始扫码添加新账号流程"""
        try:
            result = publish_application_service.start_add_account()
            status_code = 200 if result.get("success") else 500
            return json_response(result, status_code)
        except Exception as e:
            logger.error(f"开始添加账号失败: {e}")
            return json_response({"success": False, "error": str(e)}, 500)

    @publish_bp.route('/publish/accounts/check-add-status', methods=['GET'])
    def check_add_status():
        """检查扫码添加新账号是否完成"""
        try:
            result = publish_application_service.check_add_status()
            return json_response(result, 200)
        except Exception as e:
            logger.error(f"检查添加账号状态失败: {e}")
            return json_response({"success": False, "error": str(e)}, 500)

    @publish_bp.route('/publish/accounts/cancel-add', methods=['POST'])
    def cancel_add_account():
        """取消扫码添加账号并恢复此前活跃账号"""
        try:
            result = publish_application_service.cancel_add_account()
            return json_response(result, 200)
        except Exception as e:
            logger.error(f"取消添加账号失败: {e}")
            return json_response({"success": False, "error": str(e)}, 500)

    @publish_bp.route('/publish/accounts/import', methods=['POST'])
    def import_account():
        """通过导入 Cookie 添加账号"""
        try:
            data = request.get_json(silent=True) or {}
            cookie_input = data.get("cookie_input")
            alias = data.get("alias")
            if not cookie_input:
                return json_response({"success": False, "error": "Cookie 输入内容不能为空"}, 400)
            result = publish_application_service.import_account_cookies(cookie_input, alias)
            status_code = 200 if result.get("success") else 400
            return json_response(result, status_code)
        except Exception as e:
            logger.error(f"导入 Cookie 失败: {e}")
            return json_response({"success": False, "error": str(e)}, 500)

    @publish_bp.route('/publish/accounts/<account_id>', methods=['PUT'])
    def update_account_alias(account_id: str):
        """修改账号别名备注"""
        try:
            data = request.get_json(silent=True) or {}
            alias = data.get("alias", "")
            result = publish_application_service.update_account_alias(account_id, alias)
            status_code = 200 if result.get("success") else 400
            return json_response(result, status_code)
        except Exception as e:
            logger.error(f"修改账号备注失败: {e}")
            return json_response({"success": False, "error": str(e)}, 500)

    @publish_bp.route('/publish/accounts/<account_id>', methods=['DELETE'])
    def delete_account(account_id: str):
        """删除指定账号"""
        try:
            result = publish_application_service.delete_account(account_id)
            status_code = 200 if result.get("success") else 400
            return json_response(result, status_code)
        except Exception as e:
            logger.error(f"删除账号失败: {e}")
            return json_response({"success": False, "error": str(e)}, 500)

    @publish_bp.route('/publish/accounts/refresh', methods=['POST'])
    def refresh_account_status():
        """刷新指定或当前账号状态"""
        try:
            data = request.get_json(silent=True) or {}
            account_id = data.get("account_id")
            result = publish_application_service.refresh_account_status(account_id)
            return json_response(result, 200)
        except Exception as e:
            logger.error(f"刷新账号状态失败: {e}")
            return json_response({"success": False, "error": str(e)}, 500)

    # ==================== 发布功能 ====================

    @publish_bp.route('/publish/xiaohongshu', methods=['POST'])
    def publish_to_xiaohongshu():
        """
        发布内容到小红书

        请求体：
        - title: 标题（必填，最多20字）
        - content: 正文（必填）
        - images: 图片路径列表（必填）
        - tags: 标签列表（可选）

        返回：
        - success: 是否成功
        - message: 结果消息
        - post_url: 发布成功后的链接
        """
        try:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                data = {}

            title = data.get('title')
            content = data.get('content')
            images = data.get('images', [])
            tags = data.get('tags', [])

            # 参数校验
            if not title:
                return json_response({
                    "success": False,
                    "error": "标题不能为空"
                }, 400)

            if not content:
                return json_response({
                    "success": False,
                    "error": "正文不能为空"
                }, 400)

            if not images or len(images) == 0:
                return json_response({
                    "success": False,
                    "error": "至少需要一张图片"
                }, 400)

            # 执行发布
            result = publish_application_service.publish(
                title=title,
                content=content,
                images=images,
                tags=tags,
            )

            if not result.get('success'):
                if 'error' not in result and result.get('message'):
                    result['error'] = result['message']
                return json_response(result, 400)

            # 若携带历史记录 ID，自动关联写入发布历史
            record_id = data.get('record_id')
            if record_id and result.get('success'):
                try:
                    from backend.application.services import get_history_application_service
                    from backend.infrastructure.services.account_manager import get_account_manager
                    acc_mgr = get_account_manager()
                    active_acc = acc_mgr.get_active_account()
                    history_svc = get_history_application_service()
                    history_svc.add_publish_record(
                        record_id=record_id,
                        account_id=active_acc.id if active_acc else "",
                        account_name=active_acc.username if active_acc else "当前账号",
                        account_alias=active_acc.alias if active_acc else "",
                        post_url=result.get('post_url', '')
                    )
                except Exception as err:
                    logger.warning(f"自动关联历史发布记录失败: {err}")

            return json_response(result, 200)

        except Exception as e:
            logger.error(f"发布失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, 500)

    @publish_bp.route('/publish/video', methods=['POST'])
    def publish_video():
        """
        发布视频到小红书

        请求体：
        - title: 标题
        - content: 正文
        - video_path: 视频文件路径
        - cover_image: 封面图片路径（可选）
        - tags: 标签列表（可选）
        """
        try:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                data = {}

            title = data.get('title')
            content = data.get('content')
            video_path = data.get('video_path')
            cover_image = data.get('cover_image')
            tags = data.get('tags', [])

            if not title or not content or not video_path:
                return json_response({
                    "success": False,
                    "error": "标题、正文和视频路径为必填项"
                }, 400)

            result = publish_application_service.publish_with_video(
                title=title,
                content=content,
                video_path=video_path,
                cover_image=cover_image,
                tags=tags,
            )

            if not result.get('success'):
                if 'error' not in result and result.get('message'):
                    result['error'] = result['message']
                return json_response(result, 400)

            # 若携带历史记录 ID，自动关联写入发布历史
            record_id = data.get('record_id')
            if record_id and result.get('success'):
                try:
                    from backend.application.services import get_history_application_service
                    from backend.infrastructure.services.account_manager import get_account_manager
                    acc_mgr = get_account_manager()
                    active_acc = acc_mgr.get_active_account()
                    history_svc = get_history_application_service()
                    history_svc.add_publish_record(
                        record_id=record_id,
                        account_id=active_acc.id if active_acc else "",
                        account_name=active_acc.username if active_acc else "当前账号",
                        account_alias=active_acc.alias if active_acc else "",
                        post_url=result.get('post_url', '')
                    )
                except Exception as err:
                    logger.warning(f"自动关联历史发布记录失败: {err}")

            return json_response(result, 200)

        except Exception as e:
            logger.error(f"发布视频失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, 500)

    # ==================== 帖子管理 ====================

    @publish_bp.route('/publish/posts', methods=['GET'])
    def list_posts():
        """
        获取我的帖子列表

        查询参数：
        - page: 页码（默认1）
        - limit: 每页数量（默认20）
        """
        try:
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)

            result = publish_application_service.list_posts(page=page, limit=limit)

            return json_response(result, 200)
        except Exception as e:
            logger.error(f"获取帖子列表失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, 500)

    @publish_bp.route('/publish/records', methods=['GET'])
    def list_publish_records():
        """
        获取本地发布审计记录

        查询参数：
        - page: 页码（默认 1）
        - page_size: 每页数量（默认 20）
        - status: 状态过滤（可选）
        """
        try:
            page = request.args.get('page', 1, type=int)
            page_size = request.args.get('page_size', 20, type=int)
            status = (request.args.get('status') or '').strip() or None

            result = publish_application_service.list_publish_records(
                page=page,
                page_size=page_size,
                status=status,
            )
            return json_response({"success": True, **result}, 200)
        except Exception as e:
            logger.error(f"获取发布记录失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, 500)

    @publish_bp.route('/publish/search', methods=['GET'])
    def search_posts():
        """
        搜索帖子

        查询参数：
        - keyword: 搜索关键词
        - page: 页码（默认1）
        """
        try:
            keyword = request.args.get('keyword', '')
            page = request.args.get('page', 1, type=int)

            if not keyword:
                return json_response({
                    "success": False,
                    "error": "搜索关键词不能为空"
                }, 400)

            result = publish_application_service.search_posts(keyword=keyword, page=page)

            return json_response(result, 200)
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, 500)

    return publish_bp

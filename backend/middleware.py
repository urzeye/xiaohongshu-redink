"""认证与访问控制中间件"""
import logging
import os
from functools import wraps
from typing import Iterable, Optional
from flask import request, jsonify

logger = logging.getLogger(__name__)


def _get_auth_token() -> str:
    """读取访问令牌（运行时读取，支持热更新环境变量）"""
    return os.environ.get('REDINK_AUTH_TOKEN', '').strip()


def is_auth_enabled() -> bool:
    """是否启用访问令牌认证"""
    return bool(_get_auth_token())


def _validate_current_request_token():
    """校验当前请求的 Bearer Token，失败返回 Flask Response，成功返回 None"""
    auth_token = _get_auth_token()
    if not auth_token:
        return None

    # 本地回环发起的静态图片与产物 GET/HEAD 请求放行（避免桌面端 WebView 无法注入请求头或跨源 query 丢失导致的裂图）
    if request.method in ('GET', 'HEAD') and (
        request.path.startswith('/api/images/') or
        request.path.startswith('/output/') or
        (request.path.startswith('/api/history/') and request.path.endswith('/download'))
    ):
        token = request.args.get('access_token', '').strip()
        if token == auth_token:
            return None
        client_ip = request.remote_addr or ''
        if client_ip in ('127.0.0.1', '::1', 'localhost', 'testclient'):
            return None

    auth_header = request.headers.get('Authorization', '')
    token = ''
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
    elif request.method in ('GET', 'HEAD'):
        # 兼容图片、下载等浏览器直连请求：允许通过 query 传 access_token。
        token = request.args.get('access_token', '').strip()

    origin = (request.headers.get('Origin') or '').strip().rstrip('/')
    client_ip = request.remote_addr or ''
    is_local_ip = client_ip in ('127.0.0.1', '::1', 'localhost', 'testclient')
    is_tauri_origin = origin in ('tauri://localhost', 'http://tauri.localhost', 'https://tauri.localhost')

    # 本地 Tauri 桌面端发起的请求，若尚未传入 token 则放行
    if not token and is_local_ip and is_tauri_origin:
        return None

    if not token:
        return jsonify({
            'success': False,
            'error': '未提供认证令牌。请在请求头中添加 Authorization: Bearer <token>'
        }), 401

    if token != auth_token:
        logger.warning(f"认证失败: path={request.path}, ip={request.remote_addr}")
        return jsonify({
            'success': False,
            'error': '认证令牌无效'
        }), 401

    return None


def authenticate_request(exempt_paths: Optional[Iterable[str]] = None):
    """
    认证当前请求（用于全局 before_request）
    - 未设置 REDINK_AUTH_TOKEN: 直接放行
    - 设置后: 除豁免路径外要求 Bearer Token
    """
    if request.method == 'OPTIONS':
        return None

    if not is_auth_enabled():
        return None

    if exempt_paths and request.path in set(exempt_paths):
        return None

    return _validate_current_request_token()


def require_auth(f):
    """路由级认证装饰器（可选）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_result = _validate_current_request_token()
        if auth_result is not None:
            return auth_result
        return f(*args, **kwargs)

    return decorated

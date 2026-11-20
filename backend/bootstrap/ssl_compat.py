"""SSL / TLS CA 证书自愈与兼容性模块。

确保在各种打包模式、不同虚拟环境重定向或路径变动情况下，
requests / httpx / urllib3 始终能加载到有效的 CA 证书，杜绝
"Could not find a suitable TLS CA certificate bundle" 报错。
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_ca_bundle() -> str | None:
    """检测并确保 CA 证书路径有效。返回有效的 CA 文件绝对路径，若未找到返回 None。"""
    # 1. 检查当前环境或 certifi 默认路径是否已经有效
    for env_var in ("REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "SSL_CERT_FILE"):
        val = os.environ.get(env_var)
        if val and os.path.isfile(val):
            _apply_ca_bundle(val)
            return val

    try:
        import certifi
        cert_path = certifi.where()
        if cert_path and os.path.isfile(cert_path):
            _apply_ca_bundle(cert_path)
            return cert_path
    except Exception:
        pass

    # 2. 如果当前指向无效路径（例如构建输出目录被清理或路径不匹配），主动在各基准目录下全盘搜索
    project_root = Path(os.getenv("REDINK_ROOT") or Path(__file__).resolve().parents[2])
    search_dirs = [
        project_root / ".venv",
        project_root / "venv",
        Path(sys.prefix),
        Path(sys.base_prefix),
    ]

    for base in search_dirs:
        if not base.exists():
            continue
        # 直接查找标准 site-packages/certifi/cacert.pem
        direct = base / "Lib" / "site-packages" / "certifi" / "cacert.pem"
        if direct.is_file():
            _apply_ca_bundle(str(direct))
            return str(direct)
        direct_posix = base / "lib"
        for found in direct_posix.glob("python*/site-packages/certifi/cacert.pem"):
            if found.is_file():
                _apply_ca_bundle(str(found))
                return str(found)
        for found in base.glob("**/certifi/cacert.pem"):
            if found.is_file():
                _apply_ca_bundle(str(found))
                return str(found)

    logger.warning("[SSL] 未能找到本地 certifi/cacert.pem 文件")
    return None


def _apply_ca_bundle(valid_ca: str) -> None:
    """将有效 CA 文件应用至环境变量及关键网络库。"""
    os.environ["SSL_CERT_FILE"] = valid_ca
    os.environ["REQUESTS_CA_BUNDLE"] = valid_ca
    os.environ["CURL_CA_BUNDLE"] = valid_ca

    try:
        import certifi
        certifi.where = lambda: valid_ca
    except Exception:
        pass

    try:
        import requests.certs
        requests.certs.where = lambda: valid_ca
    except Exception:
        pass

    try:
        import requests.adapters
        requests.adapters.DEFAULT_CA_BUNDLE_PATH = valid_ca
    except Exception:
        pass

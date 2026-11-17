"""URL 解析与端点拼接工具函数。

提供智能处理 base_url 与 endpoint 路径拼接能力，避免版本号（如 /v1、/v3、/api/v3）重复或缺失。
"""

from __future__ import annotations

import re
from typing import Optional


def resolve_api_url(
    base_url: Optional[str],
    endpoint_type: Optional[str] = None,
    default_endpoint: str = "/v1/images/generations",
) -> str:
    """
    智能解析并拼接 API URL，避免版本号重复或缺失。

    处理规则：
    1. 规范化 base_url（去除末尾斜杠）。
    2. 规范化 endpoint（支持 'images'、'chat' 简写，确保以 '/' 开头）。
    3. 若 base_url 结尾已有版本号（如 /v1、/v2、/v3、/api/v3、/compatible-mode/v1）
       且 endpoint 开头也有版本号（如 /v1/...），则剥离 endpoint 开头的版本号，避免生成 /api/v3/v1/...。
    4. 若两者均无版本号，且 endpoint 未包含任何版本前缀，则为 endpoint 补齐 /v1。
    5. 其他情况直接拼接。

    示例：
    - ("https://api.openai.com", "/v1/images/generations") -> "https://api.openai.com/v1/images/generations"
    - ("https://api.openai.com/v1", "/v1/images/generations") -> "https://api.openai.com/v1/images/generations"
    - ("https://api.openai.com/v1", "/images/generations") -> "https://api.openai.com/v1/images/generations"
    - ("https://ark.cn-beijing.volces.com/api/v3", "/images/generations") -> "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    - ("https://ark.cn-beijing.volces.com/api/v3", "/v1/images/generations") -> "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    - ("https://dashscope.aliyuncs.com/compatible-mode/v1", "/v1/images/generations") -> "https://dashscope.aliyuncs.com/compatible-mode/v1/images/generations"
    """
    base = (base_url or "https://api.openai.com").strip().rstrip("/")
    endpoint = (endpoint_type or default_endpoint).strip()

    # 兼容旧的简写格式
    if endpoint == "images":
        endpoint = "/v1/images/generations"
    elif endpoint == "chat":
        endpoint = "/v1/chat/completions"

    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    base_has_version = bool(re.search(r"/(v\d+|api/v\d+)$", base, re.IGNORECASE))
    endpoint_has_version = bool(re.match(r"^/v\d+/", endpoint, re.IGNORECASE))

    if base_has_version and endpoint_has_version:
        # 去掉 endpoint 前缀版本号段，如 /v1/images/generations -> /images/generations
        endpoint_without_version = re.sub(r"^/v\d+", "", endpoint, flags=re.IGNORECASE)
        return f"{base}{endpoint_without_version}"
    elif not base_has_version and not endpoint_has_version:
        # 两者均无版本号段，补充默认版本 /v1
        return f"{base}/v1{endpoint}"
    else:
        return f"{base}{endpoint}"


def build_models_url(base_url: Optional[str]) -> str:
    """
    构建用于连接测试的模型列表端点 URL。

    - 对于标准 OpenAI (https://api.openai.com 或 .../v1) -> https://.../v1/models
    - 对于火山方舟 (https://ark.cn-beijing.volces.com/api/v3) -> https://.../api/v3/models
    - 对于兼容模式 (https://.../compatible-mode/v1) -> https://.../compatible-mode/v1/models
    """
    return resolve_api_url(base_url, "/v1/models", default_endpoint="/v1/models")

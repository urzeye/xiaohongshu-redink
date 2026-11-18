"""图片尺寸与宽高比解析工具。

用于将不同的宽高比（如 3:4, 16:9）和分辨率档位（如 1K, 2K, 4K）
解析为服务商（火山方舟、SiliconFlow、OpenAI DALL-E等）支持的标准尺寸字符串。
"""

from __future__ import annotations

import re
from typing import Dict, Optional

# 2K 分辨率映射表（适用于火山引擎方舟、高端文生图大模型）
# 火山引擎 Seedream 2K 标准分辨率要求宽高比合理且像素达标（如 3:4 为 1728x2304）
_RATIO_TO_SIZE_2K: Dict[str, str] = {
    "3:4": "1728x2304",
    "4:3": "2304x1728",
    "1:1": "2048x2048",
    "9:16": "1440x2560",
    "16:9": "2560x1440",
    "2:3": "1664x2496",
    "3:2": "2496x1664",
    "4:5": "1840x2300",
    "5:4": "2300x1840",
    "21:9": "3072x1312",
}

# 1K 分辨率映射表（适用于 SiliconFlow、标准 SD 等）
_RATIO_TO_SIZE_1K: Dict[str, str] = {
    "3:4": "768x1024",
    "4:3": "1024x768",
    "1:1": "1024x1024",
    "9:16": "720x1280",
    "16:9": "1280x720",
    "2:3": "768x1152",
    "3:2": "1152x768",
    "4:5": "816x1020",
    "5:4": "1020x816",
    "21:9": "1536x656",
}

# 4K 分辨率映射表
_RATIO_TO_SIZE_4K: Dict[str, str] = {
    "3:4": "2592x3456",
    "4:3": "3456x2592",
    "1:1": "4096x4096",
    "9:16": "2160x3840",
    "16:9": "3840x2160",
    "2:3": "2496x3744",
    "3:2": "3744x2496",
    "4:5": "2760x3450",
    "5:4": "3450x2760",
    "21:9": "4608x1968",
}

_TIER_TABLES = {
    "1k": _RATIO_TO_SIZE_1K,
    "2k": _RATIO_TO_SIZE_2K,
    "4k": _RATIO_TO_SIZE_4K,
    "hd": _RATIO_TO_SIZE_2K,
}


def normalize_aspect_ratio(aspect_ratio: Optional[str]) -> str:
    """标准化宽高比字符串，默认为小红书标准 3:4。"""
    if not aspect_ratio:
        return "3:4"
    normalized = str(aspect_ratio).strip().replace("：", ":").replace("/", ":")
    if ":" not in normalized:
        return "3:4"
    return normalized


def is_volcano_ark(base_url: Optional[str]) -> bool:
    """判断是否为火山引擎方舟 API。"""
    if not base_url:
        return False
    lower = base_url.lower()
    return "volces.com" in lower or "volcengine" in lower or "ark." in lower


def is_siliconflow(base_url: Optional[str]) -> bool:
    """判断是否为 SiliconFlow 硅基流动 API。"""
    if not base_url:
        return False
    return "siliconflow.cn" in base_url.lower()


def is_dall_e_3(model: Optional[str]) -> bool:
    """判断是否为 DALL-E 3 模型。"""
    if not model:
        return False
    return "dall-e-3" in model.lower()


def resolve_image_dimensions(
    aspect_ratio: Optional[str] = "3:4",
    tier: Optional[str] = "2K",
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    explicit_size: Optional[str] = None,
) -> str:
    """
    根据宽高比、清晰度档位及服务商特征，计算并返回合法的尺寸字符串 (如 "1728x2304")。

    Args:
        aspect_ratio: 宽高比，如 "3:4", "1:1", "16:9"
        tier: 尺寸档位，如 "1K", "2K", "4K", "HD"
        base_url: 接口的基础请求地址
        model: 模型名称或接入点
        explicit_size: 用户显式配置的尺寸（如果用户特意指定）

    Returns:
        尺寸规格字符串，如 "1728x2304"
    """
    ratio = normalize_aspect_ratio(aspect_ratio)

    # DALL-E 3 仅支持 1024x1024, 1024x1792, 1792x1024
    if is_dall_e_3(model):
        if ratio == "1:1":
            return "1024x1024"
        parts = ratio.split(":")
        try:
            w, h = float(parts[0]), float(parts[1])
            if h > w:
                return "1024x1792"
            else:
                return "1792x1024"
        except Exception:
            return "1024x1792"

    # 如果用户显式传入了合法且非硬编码正方形的尺寸，优先使用
    if explicit_size and isinstance(explicit_size, str):
        clean_size = explicit_size.strip().lower()
        # 若尺寸形式符合数字x数字
        if re.match(r"^\d+[x*]\d+$", clean_size):
            # 只有当用户配置的尺寸不是历史硬编码 1024x1024（当 ratio 明确要求非 1:1 时），才使用显式尺寸
            if ratio == "1:1" or clean_size not in {"1024x1024", "1024*1024"}:
                return clean_size.replace("*", "x")

    tier_key = str(tier or "2K").strip().lower()
    # 火山引擎默认偏好 2K 保证总像素 >= 3686400（满足 Seedream 4.0/5.0 要求）
    if is_volcano_ark(base_url) and tier_key not in {"1k", "2k", "4k"}:
        tier_key = "2k"

    table = _TIER_TABLES.get(tier_key, _RATIO_TO_SIZE_2K)
    if ratio in table:
        return table[ratio]

    # 未知比例：尝试动态计算
    try:
        parts = ratio.split(":")
        w_factor = float(parts[0])
        h_factor = float(parts[1])
        base_pixels = 4000000 if tier_key in {"2k", "hd"} else (1000000 if tier_key == "1k" else 8000000)
        import math
        unit = math.sqrt(base_pixels / (w_factor * h_factor))
        w = int(round((w_factor * unit) / 64) * 64)
        h = int(round((h_factor * unit) / 64) * 64)
        return f"{w}x{h}"
    except Exception:
        return table.get("3:4", "1728x2304")

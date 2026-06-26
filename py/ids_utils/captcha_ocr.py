import logging
import re

logger = logging.getLogger(__name__)
_ocr = None


def _get_ocr():
    global _ocr
    if _ocr is None:
        import ddddocr

        # old=True 对部分学校 IDS 图形验证码效果更好
        _ocr = ddddocr.DdddOcr(show_ad=False, old=True)
        logger.info("ddddocr 初始化成功")
    return _ocr


def get_ocr_res(image_bytes):
    """
    识别 IDS 验证码图片，保留大小写（部分 IDS 区分大小写）。
    """
    if not image_bytes:
        raise ValueError("验证码图片为空")

    raw = _get_ocr().classification(image_bytes)
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", raw)
    if not cleaned:
        raise ValueError(f"验证码识别结果无效: {raw!r}")
    return cleaned

import logging
import re

logger = logging.getLogger(__name__)
_ocr = None


def _get_ocr():
    global _ocr
    if _ocr is None:
        import ddddocr

        _ocr = ddddocr.DdddOcr(show_ad=False)
        logger.info("ddddocr 初始化成功")
    return _ocr


def get_ocr_res(image_bytes):
    """
    识别 IDS 验证码图片，返回小写字母数字串。
    """
    if not image_bytes:
        raise ValueError("验证码图片为空")

    raw = _get_ocr().classification(image_bytes)
    cleaned = re.sub(r"[^a-z0-9]", "", raw.lower())
    if not cleaned:
        raise ValueError(f"验证码识别结果无效: {raw!r}")
    return cleaned

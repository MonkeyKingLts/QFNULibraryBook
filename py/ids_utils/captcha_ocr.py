import io
import logging
import re
from collections import Counter

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

logger = logging.getLogger(__name__)
_ocr_models = None


def _get_ocr_models():
    global _ocr_models
    if _ocr_models is None:
        import ddddocr

        _ocr_models = [
            ("default", ddddocr.DdddOcr(show_ad=False)),
            ("old", ddddocr.DdddOcr(show_ad=False, old=True)),
        ]
        logger.info("ddddocr 初始化成功 (default + old)")
    return _ocr_models


def _image_variants(image_bytes):
    """生成多种预处理图，提高 OCR 命中率。"""
    variants = [image_bytes]
    img = Image.open(io.BytesIO(image_bytes))
    gray = img.convert("L")
    w, h = gray.size
    scale = 3 if w < 100 else 2
    big = gray.resize((w * scale, h * scale), Image.Resampling.LANCZOS)

    for enhancer_cls, factor in (
        (ImageEnhance.Contrast, 1.8),
        (ImageEnhance.Sharpness, 2.0),
        (ImageEnhance.Brightness, 1.2),
    ):
        buf = io.BytesIO()
        enhancer_cls(big).enhance(factor).save(buf, format="PNG")
        variants.append(buf.getvalue())

    sharp = big.filter(ImageFilter.SHARPEN)
    buf = io.BytesIO()
    sharp.save(buf, format="PNG")
    variants.append(buf.getvalue())

    for threshold in (100, 128, 160):
        binary = big.point(lambda p, t=threshold: 255 if p > t else 0)
        buf = io.BytesIO()
        binary.save(buf, format="PNG")
        variants.append(buf.getvalue())
        inv = ImageOps.invert(binary)
        buf = io.BytesIO()
        inv.save(buf, format="PNG")
        variants.append(buf.getvalue())

    return variants


def _normalize_captcha(text):
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", text)
    return cleaned if cleaned else None


def get_ocr_res(image_bytes):
    """
    多模型 + 多预处理图投票，选出最可能的验证码。
    """
    if not image_bytes:
        raise ValueError("验证码图片为空")

    votes = Counter()
    for variant in _image_variants(image_bytes):
        for model_name, ocr in _get_ocr_models():
            try:
                raw = ocr.classification(variant)
                cleaned = _normalize_captcha(raw)
                if not cleaned:
                    continue
                if len(cleaned) == 4:
                    votes[cleaned] += 2
                elif len(cleaned) > 4:
                    votes[cleaned[:4]] += 1
                    votes[cleaned] += 1
                else:
                    votes[cleaned] += 1
            except Exception as e:
                logger.debug(f"OCR {model_name} 失败: {e}")

    if not votes:
        raise ValueError("验证码识别无有效结果")

    best, score = votes.most_common(1)[0]
    top3 = votes.most_common(3)
    logger.info(f"验证码投票 top3: {top3}，选用: {best}")
    return best

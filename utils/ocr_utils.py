# -*- coding: utf-8 -*-
# ocr_utils.py created by MoMingLog on 14/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-14
【功能描述】
"""
from pydantic import BaseModel, Field


def slide_match(target_bytes, background_bytes):
    """
    滑动验证
    :param target_bytes: 小滑块图
    :param background_bytes: 背景图
    :return:
    """
    try:
        from ddddocr import DdddOcr
        det = DdddOcr(det=False, ocr=False, show_ad=False)
        return det.slide_match(target_bytes, background_bytes)
    except ImportError:
        raise ImportError("没有安装ddddocr模块，无法使用滑动验证")
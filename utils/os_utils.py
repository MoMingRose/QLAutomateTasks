# -*- coding: utf-8 -*-
# type_utils.py created by MoMingLog on 6/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-06
【功能描述】
"""
import os
import re

from common.base_config import TestEnvKey

try:
    import ujson as json
except:
    import json


def get_env_value(key: str | TestEnvKey) -> bool | int | float | list | dict | str | None:
    """
    将从.env中的加载的环境变量值转换为相应的数据类型
    :param key:
    :return:
    """

    if isinstance(key, TestEnvKey):
        key = key.value

    value = os.getenv(key)

    if value is None:
        return None
    # 正则表达式匹配
    if re.match(r"^(True|true)$", value):
        return True
    elif re.match(r"^(False|false)$", value):
        return False
    elif re.match(r"^\d+$", value):
        return int(value)
    elif re.match(r"^\d*\.\d*$", value):
        return float(value)
    elif re.match(r"^\[.*\]|^\{.*\}$", value):
        # 替换所有'为"
        value = value.replace("'", '"')
        return json.loads(value)
    else:
        return value


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()
    print(get_env_value(TestEnvKey.v2free))

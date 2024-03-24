# -*- coding: utf-8 -*-
# config.py created by MoMingLog on 11/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-11
【功能描述】
"""
import os

from utils.os_utils import get_env_value

# 控制台打印是否使用真实的账号/昵称，默认打印真实账号/昵称
IS_PRINT_REAL_NAME: bool = get_env_value("IS_PRINT_REAL_NAME", True)
# 消息推送是否使用真实的账号/昵称，默认推送“【账号0/1/2/3/4/5/6/7/8/9】”
IS_SEND_REAL_NAME: bool = get_env_value("IS_SEND_REAL_NAME", False)
# 是否调试运行任务，与下方调试任务列表关联
IS_DEBUG_TASKS: bool = get_env_value("IS_DEBUG_TASKS", False)
# 要调试的任务列表，与上方调试开关关联
DEBUG_TASKS_LIST: list = get_env_value("DEBUG_TASKS_LIST", [])
# 是否加密存储，默认开启
IS_ENCRYPT_SAVE: bool = get_env_value("IS_ENCRYPT_SAVE", True)
# AES加密密钥
AES_KEY: str = get_env_value("STORAGE_AES_KEY", "L*FN2m&b>CQe+=G;tVrp.S")
# webdav开关，默认关闭
WEBDAV_ENABLE: bool = get_env_value("WEBDAV_ENABLE", False)

# 项目目录
PROJECT_PATH = os.path.dirname(__file__)

# 默认的依赖对照表
DEPENDENCY_TABLE = {
    "python-dotenv": "dotenv",
    "pycryptodome": "Crypto",
}

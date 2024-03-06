# -*- coding: utf-8 -*-
# config.py created by MoMingLog on 11/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-11
【功能描述】
"""
import os

from common.base_config import BaseUserConfig, TestEnvKey
from utils.os_utils import get_env_value


class GlobalConfig:
    IS_DEBUG = True
    IS_SEND_REAL_NAME: bool = os.environ.get("IS_SEND_REAL_NAME", False) == "True"  # 是否推送真实的昵称
    PROJECT_PATH = os.path.dirname(__file__)  # 项目目录

    # 默认的依赖对照表
    DEPENDENCY_TABLE = {
        "python-dotenv": "dotenv",
        "pycryptodome": "Crypto",
    }


class DefaultUserConfig:
    V2FreeConfig = BaseUserConfig(
        # 用来标识任务名称
        tag="V2Free",
        # 环境变量中存放账号数据的key（会按照这个值来查找，可以自定义）
        env_key="v2free_userinfo",
        # 测试环境下的环境变量值（从.env文件中获取）
        test_env=get_env_value(TestEnvKey.v2free)
    )

    MIUIVERConfig = BaseUserConfig(
        tag="MIUI历史版本（刷机包）",
        test_env=get_env_value(TestEnvKey.miuiver)
    )

    JMKJConfig = BaseUserConfig(
        tag="芥末空间",
        test_env=get_env_value(TestEnvKey.jmkj)
    )

    MTConfig = BaseUserConfig(
        tag="MT论坛",
        test_env=get_env_value(TestEnvKey.mt)
    )

    TYYPConfig = BaseUserConfig(
        tag="天翼云盘",
        test_env=get_env_value(TestEnvKey.tyyp)
    )

    HLXConfig = BaseUserConfig(
        tag="葫芦侠三楼",
        test_env=get_env_value(TestEnvKey.hlx)
    )

    ALYPConfig = BaseUserConfig(
        tag="阿里云盘",
        test_env=get_env_value(TestEnvKey.alyp)
    )

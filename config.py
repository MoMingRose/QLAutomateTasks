# -*- coding: utf-8 -*-
# config.py created by MoMingLog on 11/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-11
【功能描述】
"""
import os

from common.base_config import BaseUserConfig, BaseTokenConfig


class GlobalConfig:
    IS_DEBUG = True


class DefaultUserConfig:
    MIUIVER = BaseUserConfig(tag="MIUI历史版本（刷机包）", env_key="miuiver_userinfo", test_env=os.environ.get("MIUIVER"))
    JMKJConfig = BaseUserConfig(tag="芥末空间", env_key="jmkj_userinfo", test_env=os.environ.get("JMKJ"))
    MTConfig = BaseUserConfig(tag="MT论坛", env_key="mt_userinfo", test_env=os.environ.get("MT"))
    V2FreeConfig = BaseUserConfig(tag="V2free", test_env=os.environ.get("V2FREE"))
    TYYPConfig = BaseUserConfig(tag="天翼云盘", env_key="tyyp_userinfo", test_env=os.environ.get("TYYP"))
    HLXConfig = BaseUserConfig(tag="葫芦侠三楼", env_key="hlx_userinfo", test_env=os.environ.get("HLX"))

    ALYPConfig = BaseTokenConfig(tag="阿里云盘", env_key="alyp_userinfo", test_env=os.environ.get("ALYP"))

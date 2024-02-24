# -*- coding: utf-8 -*-
# base_config.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""
from pydantic import BaseModel, Field


class BaseConfig(BaseModel):
    """
    基础配置信息
    """
    tag: str = Field(..., description="哪一个任务的标签")
    env_key: str = Field(default=None, description="系统环境变量的key")
    test_env: str = Field(default=None, description="测试的环境变量值")


class BaseUserConfig(BaseConfig):
    """
    基础配置信息
    """
    username: str = Field(default=None, description="账号")
    password: str = Field(default=None, description="密码")
    account_list: list = Field(default=None, description="账号列表")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.env_key = kwargs.get("env_key")
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.account_list = kwargs.get("account_list")
        self.test_env = kwargs.get("test_env")


class BaseTokenConfig(BaseConfig):
    nickname: str = Field(default=None, description="昵称，用于标识用户token")
    token: str = Field(default=None, description="能代表用户身份的字符串")
    token_list: list = Field(default=None, description="token列表，多个用户")

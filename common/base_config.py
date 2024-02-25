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
    env_key: str | None = Field(default=None, description="账号传递方式：系统环境变量的key，支持多账号传递")
    test_env: str | None = Field(default=None, description="账号传递方式：测试的环境变量值")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.env_key = kwargs.get("env_key")
        self.test_env = kwargs.get("test_env")


class BaseUserConfig(BaseConfig):
    """
    基础配置信息
    """
    username: str | None = Field(default=None, description="单账号传递方式：账号（与password配合）")
    password: str | None = Field(default=None, description="单账号传递方式：密码（与username配合）")
    account_list: list = Field(default=[], description="多账号传递方式：账号列表")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.account_list = kwargs.get("account_list")

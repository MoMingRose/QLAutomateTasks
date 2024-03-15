# -*- coding: utf-8 -*-
# base_config.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""

from pydantic import BaseModel, Field


class BaseUserConfig(BaseModel):
    """
    基础配置信息
    """
    env_key: str | None = Field(default=None, description="账号传递方式：系统环境变量的key，支持多账号传递")
    username: str | None = Field(default=None, description="单账号传递方式：账号（与password配合）")
    password: str | None = Field(default=None, description="单账号传递方式：密码（与username配合）")
    up_split: str = Field(default="&", description="账号密码间的分隔符")
    ups_split: str = Field(default="|", description="多个账号之间的分隔符")
    account_list: list = Field(default=[], description="多账号传递方式：账号列表")


class BaseTaskConfig(BaseUserConfig):
    task_name: str = Field(default="", description="任务名称")
    task_desc: str = Field(default="", description="任务描述")
    task_enable: bool = Field(default=True, description="是否可用")

# -*- coding: utf-8 -*-
# base_config.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""

from pydantic import BaseModel, Field

from utils.os_utils import get_env_value


class BaseUserConfig(BaseModel):
    """
    基础配置信息
    """
    env_key: str | None = Field(default=None, description="账号传递方式：系统环境变量的key，支持多账号传递")
    username: str | None = Field(default=None, description="单账号传递方式：账号（与password配合）")
    password: str | None = Field(default=None, description="单账号传递方式：密码（与username配合）")
    load_strategy: int = Field(
        default=get_env_value("LOAD_STRATEGY", 1),
        description="加载策略（读取用户配置数据：包含cookie或其他重要数据，任务完成时间等）"
    )
    save_strategy: list = Field(
        default=get_env_value("SAVE_STRATEGY", [1]),
        description="存储策略（将用户配置数据储存到何处）"
    )
    up_split: str = Field(default="&", description="账号密码间的分隔符")
    ups_split: str = Field(default="|", description="多个账号之间的分隔符")
    account_list: list = Field(default=[], description="多账号传递方式：账号列表")


class BaseTaskConfig(BaseUserConfig):
    task_name: str = Field(default="", description="任务名称")
    task_desc: str = Field(default="", description="任务描述")
    task_enable: bool = Field(default=True, description="是否可用")


class WebDavConfig(BaseModel):
    base_url: str = Field(
        get_env_value("WEBDAV_BASE_URL"),
        description="WebDav服务器地址, 例如：http://192.168.99.99:5244/dav"
    )
    username: str = Field(
        get_env_value("WEBDAV_USER"),
        description="WebDav用户名"
    )
    password: str = Field(
        get_env_value("WEBDAV_PWD"),
        description="WebDav密码"
    )
    base_remote_dir: str = Field(
        get_env_value("WEBDAV_BASE_DIR", "/"),
        description="WebDav的基本远程目录，例如：/MoMingLog/NAS/QL"
    )

# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""
from .cloudpan import CLOUD_PAN_TASKS
from .forum import FORUM_TASKS
from .resource import RESOURCE_TASKS

WEB_TASKS = FORUM_TASKS + CLOUD_PAN_TASKS + RESOURCE_TASKS

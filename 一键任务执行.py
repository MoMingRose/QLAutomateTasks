# -*- coding: utf-8 -*-
# 一键任务执行.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】统一运行签到任务的入口
【功能描述】
"""
import os

try:
    import ujson as json
except:
    import json

from utils.base_utils import global_run
from utils.base_utils import msg_list
from utils.os_utils import get_env_value

if __name__ == '__main__':
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except:
        pass
    from software import *
    from web import *

    tasks = WEB_TASKS + SOFTWARE_TASKS

    for task in tasks:
        if get_env_value("IS_DEBUG_TASKS"):
            if task.TAG not in get_env_value("DEBUG_TASKS_LIST"):
                continue
        global_run(task, task.TAG)

    from notify import send

    send("MoMingLog自动任务通知", "\n".join(msg_list))
    msg_list.clear()

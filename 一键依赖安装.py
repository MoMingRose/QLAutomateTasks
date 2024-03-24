# -*- coding: utf-8 -*-
# 一键依赖安装.py created by MoMingLog on 27/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-27
【功能描述】
"""
from global_config import DEPENDENCY_TABLE
from utils.project_utils import check_and_install_dependencies

if __name__ == '__main__':
    # 如果需要添加新的对照表可以在这里添加
    DEPENDENCY_TABLE.update({

    })

    check_and_install_dependencies()

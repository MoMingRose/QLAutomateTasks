# -*- coding: utf-8 -*-
# project_utils.py created by MoMingLog on 27/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-27
【功能描述】
"""
import subprocess

import global_config


def generate_requirements(dir: str = global_config.PROJECT_PATH) -> None:
    """
    通过pipreqs库，生成依赖项列表

    使用前需要安装库： `pip install pipreqs`

    :param dir: 存放目录
    :return:
    """
    try:
        subprocess.run(["pipreqs", dir, "--encoding=utf-8", "--force"])
        print("依赖项列表已生成成功！")
    except Exception as e:
        print(f"生成依赖项列表时出错：{e}")


def get_required_packages(
        folder_path: str = global_config.PROJECT_PATH,
        file_name: str = "requirements.txt"
) -> list:
    """
    获取依赖包
    :param folder_path:
    :param file_name:
    :return:
    """
    with open(f"{folder_path}/{file_name}", "r") as f:
        pack_list = []
        for line in f:
            if install_name := line.strip().lower():
                import_name = install_name.split("==")[0]
                pack_list.append((install_name, global_config.DEPENDENCY_TABLE.get(import_name, import_name)))
        return pack_list


def check_and_install_dependencies(
        folder_path: str = global_config.PROJECT_PATH,
        file_name: str = "requirements.txt"
):
    """
    检查并安装依赖
    :param folder_path:
    :param file_name:
    :return:
    """
    required_packages = get_required_packages(
        folder_path=folder_path,
        file_name=file_name
    )

    missing_packages = []
    for install_name, import_name in required_packages:
        try:
            # 尝试导入包，如果导入失败则说明缺少该包
            __import__(import_name)
        except ImportError:
            missing_packages.append(install_name)

    if missing_packages:
        print("当前环境缺少以下依赖：", missing_packages)
        try:
            # 使用pip3安装缺失的包
            for package in missing_packages:
                subprocess.run(["pip3", "install", package])
            print("依赖项安装成功！")
        except Exception as e:
            print(f"安装依赖项时出错：{e}")
    else:
        print("当前环境已安装所有项目依赖。")

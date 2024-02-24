# -*- coding: utf-8 -*-
# base_utils.py created by MoMingLog on 13/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-13
【功能描述】
"""

import os

msg_list = []


def global_run(obj, tag: str, arg=None):
    print(f"开始{tag}签到任务".center(50, "-"))
    msg_list.append(f"开始{tag}签到任务".center(20, "-"))
    try:
        if arg:
            msg_list.append(obj(arg).result())
        else:
            msg_list.append(obj().result())
    except Exception as e:
        print(f"{tag}签到任务出现异常：{e}")
        msg_list.append(f"{tag}签到任务出现异常：{e}")

    print(f"结束{tag}签到任务".center(50, "-"))
    msg_list.append(f"结束{tag}签到任务".center(20, "-"))
    print()


def fetch_account_list(env_key: str = None, test_env: str = None) -> list:
    """
    从环境变量中获取账号密码列表
    :param env_key: 环境变量key
    :param test_env: 需要测试的环境变量值
    :return: 账号密码列表
    """
    account_list = []
    # 测试环境变量值优先原则
    userinfo = os.getenv(env_key) if test_env is None else test_env
    # 判断环境变量中是否存在账号密码
    if userinfo is not None:
        # 判断格式是否正确
        if "&" not in userinfo:
            raise AttributeError("单账号密码格式错误：缺少“&”")
        if userinfo.count("&") != userinfo.count("|") + 1:
            raise AttributeError(
                f"多账号密码格式错误，“&”与“|”符号数量不匹配\n\n检测“&”数量为：{userinfo.count('&')}个\n检测“|”数量为：{userinfo.count('|')}\n\n“|”+1 不等于 “&”")

        # 判断是否存在|，存在则进行分割
        if "|" in userinfo:
            # 表示环境变量中存在多账号密码，进行账号分割
            userinfo_list = userinfo.split("|")
            # 遍历账号密码列表，进行账号密码分割
            for i in userinfo_list:
                # 添加到账号列表中
                account_list.append(i.split("&"))
        else:
            # 表示环境变量中只存在单账号密码，进行账号密码分割
            # 添加到账号列表中
            account_list.append(userinfo.split("&"))
    else:
        # 不存在账号密码，抛出异常
        raise AttributeError(f"未在环境变量 {env_key} 中找到账号密码")
    return account_list


def get_today():
    """
    获取今天的日期
    :return:
    """
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")

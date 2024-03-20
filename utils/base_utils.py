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
    print(f"开始{tag}任务".center(20, "🟢"))
    msg_list.append(f"开始{tag}任务".center(15, "🔆"))

    is_pop = False

    try:
        if arg:
            msg = obj(arg).result
        else:
            msg = obj().result

        if "任务不可用" in msg:
            msg_list.pop()
            is_pop = True
        else:
            msg_list.append(msg)
    except Exception as e:
        raise e
        print(f"{tag}任务出现异常：{e}")
        msg_list.append(f"‼️‼️{tag}任务出现异常：{e}")

    print(f"结束{tag}任务".center(20, "🟢"))
    if not is_pop:
        msg_list.append(f"结束{tag}任务".center(15, "🔆"))
        msg_list.append(" ")
    print()


def fetch_account_list(env_key: str = None, up_split: str = "&", ups_split: str = "|") -> list:
    """
    从环境变量中获取账号密码列表
    :param env_key: 环境变量key
    :param up_split: 账号密码间的分隔符
    :param ups_split: 多个账号之间的分隔符
    :return: 账号密码列表
    """
    account_list = []

    # 判断env_key中是否存在 _
    if "_" in env_key:
        # 如果存在，则提取出分隔符key前缀
        split_key_prefix = env_key.split("_")[0]
        # 使用分隔符key前缀拼接
        up_split_key = f"{split_key_prefix}_up"
        ups_split_key = f"{split_key_prefix}_ups"
    else:
        # 否则使用自定义env_key拼接
        up_split_key = f"{env_key}_up"
        ups_split_key = f"{env_key}_ups"

    # 从环境变量中获取分隔符，如果环境变量不存在，则使用传入的分隔符
    up_split = os.getenv(up_split_key, up_split)
    ups_split = os.getenv(ups_split_key, ups_split)

    # 测试环境变量值优先原则
    userinfo = os.getenv(env_key)
    # 判断环境变量中是否存在账号密码
    if userinfo is not None:
        # 判断账号密码分隔符是否不存在
        if up_split not in userinfo:
            # 不存在则抛出异常
            raise AttributeError(f"单账号密码格式错误：请用“{up_split}”分离账号密码")
        # 存在则判断账号密码分隔符与多账号分隔符数量是否匹配
        if userinfo.count(up_split) != userinfo.count(ups_split) + 1:
            # 如果不匹配，则抛出异常
            raise AttributeError(f'''多账号密码格式错误： 请用“{ups_split}”分离多个账号
    检测“{up_split}”数量为：{userinfo.count(up_split)}
    检测“{ups_split}”数量为：{userinfo.count(ups_split)}
    “{ups_split}”+1 不等于 “{up_split}”''')

        # 判断是否存在多账号分隔符，存在则进行分割
        if ups_split in userinfo:
            # 表示环境变量中存在多账号密码，进行账号分割
            userinfo_list = userinfo.split(ups_split)
            # 遍历账号密码列表，进行账号密码分割
            for i in userinfo_list:
                # 添加到账号列表中
                account_list.append(i.split(up_split))
        else:
            # 表示环境变量中只存在单账号密码，进行账号密码分割
            # 添加到账号列表中
            account_list.append(userinfo.split(up_split))
    else:
        # 不存在账号密码，抛出异常
        raise AttributeError(f"未在环境变量 {env_key} 中找到账号数据")
    return account_list


def get_today():
    """
    获取今天的日期
    :return:
    """
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")

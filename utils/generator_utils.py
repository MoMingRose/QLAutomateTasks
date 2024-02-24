# -*- coding: utf-8 -*-
# generator_utils.py created by MoMingLog on 14/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-14
【功能描述】
"""
import random
import time


def uuid_generator(length: int = 16):
    """
    随机生成16位的UUID
    :return:
    """
    a = "abcdefghijklmnopqrstuvwxyz0123456789"

    uuid_str = ""

    for i in range(length):
        uuid_str += a[random.randint(0, len(a) - 1)]

    return uuid_str


def rates_generator(correct_point_x):
    """
    生成移动轨迹
    :param correct_point_x: 滑块正确位置
    :return:
    """
    current_x = 0  # 初始化滑块的当前位置
    rates = []  # 存储移动轨迹数据的列表
    drag_time = 0  # 模拟拖动所花费的时间
    flag = True  # 是否需要回退

    while current_x != correct_point_x:
        # 计算当前位置与正确位置之间的距离
        distance = correct_point_x - current_x

        # 确定滑块每次移动的距离
        move = random.randint(1, min(4, distance))  # 正数移动

        # 模拟移动所花费的时间，使用随机时间模拟
        time_taken = random.randint(1, 30)
        drag_time += time_taken

        # 更新当前位置
        if distance < 10 and flag:
            for i in range(5):
                move = random.randint(1, min(4, distance))
                current_x -= move
                rates.append({'pointDiff': -1 * move, 'timeDiff': time_taken})
            flag = False
        else:
            current_x += move
            # 将移动距离和时间添加到轨迹数据中
            rates.append({'pointDiff': move, 'timeDiff': time_taken})
    return {
        "rates": rates,
        "dragTime": drag_time,
        "time": int(time.time() * 1000)
    }

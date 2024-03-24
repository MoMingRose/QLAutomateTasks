# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 14/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-14
【功能描述】
"""
import re
import time
from typing import Tuple

import task_config
from common.base import BaseFSTemplateForCookie
from common.base_config import BaseTaskConfig


class V2EX(BaseFSTemplateForCookie):
    DEFAULT_TASK_CONFIG = task_config.V2EXConfig
    TAG = DEFAULT_TASK_CONFIG.task_name

    def __init__(self, taskConfig: BaseTaskConfig = DEFAULT_TASK_CONFIG):
        self.once = None
        # self.is_enable_sign = True
        self.is_sign = False
        self.current_balance = None
        self.new_current_balance = None
        super().__init__(taskConfig, "v2ex_userinfo")

    def sign_task_run(self, nickname: str, token: str, *args, **kwargs) -> bool:
        if self.is_sign:
            self.push_msg("今日已签到，跳过此任务")
            return True

        # if not self.is_enable_sign:
        #     self.push_msg("签到功能已关闭，跳过此任务")
        #     return True

        if self.once is None:
            raise Exception("once提取失败，请检查代码!")

        url = f"https://www.v2ex.com/mission/daily/redeem?once={self.once}"
        res = self.session.get(url, timeout=5)
        html = res.text
        self.new_current_balance = self.__fetch_balance_val(html)
        if "已成功领取" in html:
            return True
        return False

    def check_cookie_is_expire(self) -> bool:
        # 测试时发现“没有签到，却显示已签到，且主页没有签到入口”的情况
        # 故尝试先请求一下主页
        homepage = self.__request_homepage()
        # 判断cookie是否过期
        if not all([r in homepage for r in ["记事本", "时间轴", "设置"]]):
            # 只要其中一个不存在，则表示过期（目的是预防帖子中出现重试字眼）
            return True

        # 提取当前账户余额
        self.current_balance = self.__fetch_balance_val(homepage)

        # 接下来就是在cookie没有过期的情况下，进行一些数据参数初始化
        # if "领取今日的登录奖励" not in homepage:
        #     self.is_enable_sign = False
        daily_page = self.__request_daily_page()
        if "每日登录奖励已领取" in daily_page:
            self.is_sign = True

        # 提取签到链接参数数据
        if r := re.search(r"redeem\?once=(.*?)'", daily_page, re.S):
            self.once = r.group(1)
        return False

    def build_base_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://www.v2ex.com"
        }

    def get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        return "cookie", current_user_config_data["cookie"], True

    def other_task_run(self, *args, **kwargs) -> bool:
        pass

    def last_task_run(self, *args, **kwargs):
        if self.new_current_balance is None:
            html = self.__request_balance_page()
            # 提取当前余额
            self.current_balance = self.__fetch_balance_val(html)
            self.push_msg(f"今日登录奖励：{self.__fetch_login_reward(html)}铜币")
        else:
            self.push_msg(f"今日登录奖励：{self.new_current_balance - self.current_balance}铜币")
            self.current_balance = self.new_current_balance

        self.push_msg(f"当前余额为: {self.current_balance}铜币")

    def __request_homepage(self):
        return self.__request_page("https://www.v2ex.com/")

    def __request_daily_page(self):
        return self.__request_page("https://www.v2ex.com/mission/daily")

    def __request_balance_page(self):
        return self.__request_page("https://www.v2ex.com/balance")

    def __request_page(self, url):
        return self.session.get(url, timeout=5).text

    @staticmethod
    def __fetch_login_reward(html: str):
        # 获取当前时间，时间格式为 年-月-日
        now = time.strftime("%Y-%m-%d", time.localtime())
        # 提取所有的登录奖励和时间
        all_rewards = re.findall(r"(\d{4}-\d{2}-\d{2}).*?(?:奖励|资本).*?<strong>(\d+\.\d+)</strong>", html, re.S)
        # 计算今日登录奖励并返回
        return sum(float(reward) for date, reward in all_rewards if date == now)

    @staticmethod
    def __fetch_balance_val(html: str):
        # 编译正则表达式模式
        balance_pattern = re.compile(r"<a.*?balance_area.*?>(.*?)</a>", re.S)
        coin_pattern = re.compile(r"\d+")

        gold_coin = silver_coin = bronze_coin = 0

        # 搜索余额区域
        if match := balance_pattern.search(html):
            balance_area = match.group(1)

            # 删除所有图片标签
            all_coin_text = re.sub(r"<img.*?>", "", balance_area)

            # 查找所有硬币类型及其数量
            all_coin_list = coin_pattern.findall(all_coin_text)
            num_coins = len(all_coin_list)

            # 根据硬币数量赋值金、银、铜硬币数量
            if num_coins == 3:
                gold_coin, silver_coin, bronze_coin = map(int, all_coin_list)
            elif num_coins == 2:
                silver_coin, bronze_coin = map(int, all_coin_list)
            elif num_coins == 1:
                bronze_coin = int(all_coin_list[0])

        # 计算总余额
        total_balance = gold_coin * 10000 + silver_coin * 100 + bronze_coin
        return total_balance

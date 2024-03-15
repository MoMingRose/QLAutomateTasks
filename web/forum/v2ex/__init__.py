# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 14/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-14
【功能描述】
"""
import re
from typing import Tuple

import config
from common.base import BaseFSTemplateForCookie
from common.base_config import BaseTaskConfig


class V2EX(BaseFSTemplateForCookie):
    DEFAULT_TASK_CONFIG = config.DefaultTaskConfig.V2EXConfig
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
        self.new_current_balance = self.__fetch_balance(html)
        if "已成功领取" in html:
            return True
        return False

    def check_cookie_is_expire(self) -> bool:
        # 测试时发现“没有签到，却显示已签到，且主页没有签到入口”的情况
        # 故尝试先请求一下主页
        homepage = self.__request_homepage()

        # 判断cookie是否过期
        if not all([r in homepage for r in ["记事本", "时间轴", "设置"]]):
            # 只要其中一个不存在，则表示过期
            return True

        # 提取当前账户余额
        self.current_balance = self.__fetch_balance(homepage)

        # 接下来就是在cookie没有过期的情况下，进行一些数据参数初始化
        # if "领取今日的登录奖励" not in homepage:
        #     self.is_enable_sign = False
        daily_page = self.__request_daily()
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
        if self.current_balance is not None and self.new_current_balance is not None:
            self.push_msg(f"今日签到奖励：{int(self.new_current_balance) - int(self.current_balance)}铜币")
        elif self.new_current_balance is None:
            balance = self.__request_balance()
            self.push_msg(f"今日签到奖励：{balance}铜币")

        self.push_msg(f"当前余额为: {self.current_balance}铜币")

    def __request_homepage(self):
        url = "https://www.v2ex.com/"
        res = self.session.get(url, timeout=5)
        return res.text

    def __request_daily(self):
        url = "https://www.v2ex.com/mission/daily"
        res = self.session.get(url, timeout=5)
        return res.text

    def __request_balance(self):
        url = "https://www.v2ex.com/balance"
        html = self.session.get(url, timeout=5).text
        self.current_balance = self.__fetch_balance(html)
        if r := re.search(r"<span.*?奖励.*?(\d+).*?<", html, re.S):
            return r.group(1)

    def __fetch_balance(self, html: str):
        if r := re.search(r"<a.*?balance_area.*?>(\d+).*?<", html, re.S):
            return r.group(1)

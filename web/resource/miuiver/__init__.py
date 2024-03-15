# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 24/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-24
【功能描述】
"""
import re
from typing import Tuple

import config
from common.base import BaseFSTemplateForAccount
from common.base_config import BaseTaskConfig


class MIUIVER(BaseFSTemplateForAccount):
    DEFAULT_TASK_CONFIG = config.DefaultTaskConfig.MIUIVERConfig
    TAG = DEFAULT_TASK_CONFIG.task_name

    def __init__(self, taskConfig: BaseTaskConfig = DEFAULT_TASK_CONFIG):
        self.html = None
        super().__init__(taskConfig, "miuiver_userinfo")

    def build_base_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
            "Accept": "application/json;charset=UTF-8"
        }

    def fetch_primary_data(self, username: str, password: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        """
        这里是通过登录来获取主要数据（cookie）
        :return: 这里返回是否登录成功
        """
        url = "https://miuiver.com/wp-content/plugins/erphplogin//action/login.php"
        data = {
            "log": username,
            "pwd": password,
            "action": "mobantu_login"
        }

        response = self.session.post(url, data=data, timeout=5)
        result = response.text
        if result in ["1", 1]:
            # return "cookie", self.session.cookies.get_dict(), True
            return True
        return False

    def get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        """
        这里的主要数据是cookie
        :param current_user_config_data: 
        :return: 
        """
        # 将cookie设置为主要参数，并且写入请求头
        return "cookie", current_user_config_data["cookie"], True

    def check_expire_task_run(self) -> bool:
        """
        检查cookie是否过期
        :return: 
        """
        self.html = self.__request_user_profile()
        if not self.html and "退出登录" not in self.html:
            self.html = None
            return True
        return False

    def sign_task_run(self, username: str, password: str, *args, **kwargs) -> bool:
        """
        签到任务的具体实现
        :param username: 账号
        :param password: 密码
        :param args: 
        :param kwargs: 
        :return: 
        """
        url = "https://miuiver.com/wp-admin/admin-ajax.php"
        data = {
            "action": "epd_checkin"
        }
        response = self.session.post(url, data=data, timeout=5)
        try:
            res_json = response.json()
            status = res_json.get("status")
            if status == 200:
                self.push_msg("签到成功! 获得固定1积分")
            elif status == 201:
                self.push_msg("今日已签到!")
            else:
                return False
            return True
        except Exception as e:
            self.push_msg(response.text)
            return False

    def other_task_run(self, *args, **kwargs) -> bool:
        pass

    def last_task_run(self, *args, **kwargs):
        html = self.html if self.html else self.__request_user_profile()
        try:
            # 提取当前积分
            current_point = re.search(r'当前积分.*?(\d+).*?', html, re.S).group(1)
            # 提取已用积分
            used_point = re.search(r'已用积分.*?(\d+).*?', html, re.S).group(1)
            self.push_msg(f"当前积分: {current_point}, 已用积分: {used_point}")
        except:
            self.push_msg("积分详情提取失败，请更新正则!")

    def __request_user_profile(self) -> str:
        """
        获取用户信息
        :return:
        """
        url = "https://miuiver.com/user-profile/"
        response = self.session.get(url, timeout=5)
        return response.text

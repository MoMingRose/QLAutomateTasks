# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 24/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-24
【功能描述】
"""
import os.path

import config
from common.base import LoginAndSignTemplate
from common.base_config import BaseUserConfig


class MIUIVER(LoginAndSignTemplate):
    MIUIVER_DEFAULT_USER_CONFIG = config.DefaultUserConfig.MIUIVER
    TAG = MIUIVER_DEFAULT_USER_CONFIG.tag

    def __init__(self, userConfig: BaseUserConfig = MIUIVER_DEFAULT_USER_CONFIG):
        super().__init__(userConfig, "miuiver_userinfo")

    def _set_files_dir(self):
        return os.path.dirname(__file__)

    def _check_expire(self) -> bool:
        url = "https://miuiver.com/user-profile/?action=info"
        response = self.session.get(url)
        html = response.text
        if "退出登录" not in response.text:
            return True
        return False

    def _sign(self):
        url = "https://miuiver.com/wp-admin/admin-ajax.php"
        data = {
            "action": "epd_checkin"
        }
        response = self.session.post(url, data=data)
        try:
            res_json = response.json()
            status = res_json.get("status")
            if status == 200:
                self.print("签到成功! 获得固定1积分")
            elif status == 201:
                self.print("今日已签到!")
            else:
                return False
            return True

        except Exception as e:
            self.print(response.text)
            return False

    def _login(self):
        url = "https://miuiver.com/wp-content/plugins/erphplogin//action/login.php"
        data = {
            "log": "MoMingLog",
            "pwd": "C4PHybk@h2KxC8J",
            "action": "mobantu_login"
        }

        response = self.session.post(url, data=data)
        result = response.text
        if result in ["1", 1]:
            return True
        return False

# import requests
#
#
# payload = "log=test&pwd=test&action=mobantu_login"
#
#
#
#
#
# response = requests.post(url, data=data, headers=headers)
#
# try:
#     print(response.json())
# except Exception as e:
#     print(response.text)

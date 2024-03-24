# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 22/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-22
【功能描述】
"""
import re
from typing import Tuple

import task_config
from common.base import BaseFSTemplateForAccount
from common.base_config import BaseTaskConfig


class XKProxy(BaseFSTemplateForAccount):
    XKProxy_DEFAULT_TASK_CONFIG = task_config.XKProxyConfig
    TAG = XKProxy_DEFAULT_TASK_CONFIG.task_name

    def __init__(self, taskConfig: BaseTaskConfig = XKProxy_DEFAULT_TASK_CONFIG):
        self.current_balance = None
        self.current_exp = 0
        self.full_exp = 0
        self.vip_level = 1
        self.vip_name = "普通会员"
        super().__init__(taskConfig, "xkdl_userinfo")

    def fetch_primary_data(self, username: str, password: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        url = "https://www.xkdaili.com/tools/submit_ajax.ashx?action=user_login&site_id=1"
        payload = f"username={username}&password={password}&remember=1&code="
        try:
            res_json = self.session.post(url, data=payload).json()
            if res_json["status"] == 1:
                return True
            else:
                return False
        except:
            return False

    def build_base_headers(self) -> dict:
        return {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Content-Type': "application/x-www-form-urlencoded",
            'origin': "https://www.xkdaili.com",
            'referer': "https://www.xkdaili.com/",
        }

    def get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        return "cookie", current_user_config_data["cookie"], True

    def check_expire_task_run(self) -> bool:
        html = self.__request_user_center()
        if "欢迎回来" in html:
            self.__init_data(html)
            return False
        return True

    def sign_task_run(self, *args, **kwargs) -> bool:
        url = "https://www.xkdaili.com/tools/submit_ajax.ashx?action=user_receive_point"
        payload = "type=login"

        try:
            res_json = self.session.post(url, data=payload).json()
            if res_json["status"] == 1:
                msg_json = res_json["msg"]
                # 增加的经验值
                exp = msg_json["exp"]
                # 此次签到获得的星币
                point = msg_json["point"]
                # 当前等级
                self.vip_level = msg_json["grade"]
                # 当前会员名称
                self.vip_name = msg_json["gradename"]
                # 当前等级阶段需要升级的总经验值
                self.full_exp = msg_json["growfull"]
                self.current_balance += point
                self.current_exp += exp
                self.push_msg(
                    f"签到成功! \n> 获得星币: {point}\n> 当前星币: {self.current_balance}\n> 获得经验: {exp}\n> 当前等级: {self.vip_level}_{self.vip_name}\n> 升级经验: 需{self.full_exp}, 还差 {self.full_exp - self.current_exp}")
                return True
            elif res_json["status"] == 0:
                self.push_msg(f"签到失败, {res_json['msg']}")
                return True
            else:
                return False
        except Exception as e:
            self.push_msg(f"签到失败:", str(e), is_push=False)
            return False

    def other_task_run(self, *args, **kwargs) -> bool:
        pass

    def last_task_run(self, *args, **kwargs):
        if self.current_balance is None:
            self.__init_data(self.__request_user_center())
        self.push_msg(
            f"统计情况如下：\n> 当前星币: {self.current_balance}\n> 当前经验: {self.current_exp}\n> 当前等级: {self.vip_level}_{self.vip_name}\n> 升级经验: 需{self.full_exp}, 还差 {self.full_exp - self.current_exp}")

    def __init_data(self, html):
        self.current_balance = self.__fetch_current_balance(html)
        self.current_exp = self.__fetch_current_exp(html)
        self.full_exp = self.__fetch_full_exp(html)
        self.vip_level = self.__fetch_vip_level(html)
        self.vip_name = self.__fetch_vip_name(html)

    def __request_user_center(self) -> str:
        url = "https://www.xkdaili.com/main/usercenter.aspx"
        return self.session.get(url).text

    def __fetch_current_balance(self, html):
        return self.__fetch_common(html, r'star_B_Num">(\d+)</span>', "星币余额")

    def __fetch_current_exp(self, html) -> int:
        return int(self.__fetch_common(html, r'progressBar_Num">(\d+)</span', "当前经验"))

    def __fetch_full_exp(self, html) -> int:
        return int(self.__fetch_common(html, r'progressBar_ALLNum">(\d+)</span', "升级经验"))

    def __fetch_vip_level(self, html) -> int:
        return int(self.__fetch_common(html, r'VIP_Img.*?VIP(\d).png', "会员等级"))

    def __fetch_vip_name(self, html) -> str:
        return self.__fetch_common(html, r'"VipName">(.*?)</li>', "会员名称")

    @staticmethod
    def __fetch_common(html, pattern, tag=""):
        if r := re.search(pattern, html):
            return r.group(1)
        else:
            raise AttributeError(f"提取{tag}失败，请更新正则表达式!")

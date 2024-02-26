# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""
import re
from typing import Tuple

import config
from common.base_config import BaseUserConfig
from common.base import BaseFileStorageTemplateForAccount


class MT(BaseFileStorageTemplateForAccount):
    MT_DEFAULT_USER_CONFIG = config.DefaultUserConfig.MTConfig
    TAG = MT_DEFAULT_USER_CONFIG.tag

    def __init__(self, userConfig: BaseUserConfig = MT_DEFAULT_USER_CONFIG):
        super().__init__(
            userConfig,
            "mt_userinfo"
        )

    def fetch_primary_data(self, username: str, password: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        url = "https://bbs.binmt.cc/member.php"

        formhash, loginhash = self.__fetch_login_hash_value()

        params = {
            "mod": "logging",
            "action": "login",
            "loginsubmit": "yes",
            "handlekey": "login",
            "loginhash": loginhash,
            "inajax": "1",
        }

        data = {
            "formhash": formhash,
            "referer": "https://bbs.binmt.cc/forum.php?mod=guide",
            "loginfield": "username",
            "username": self._username,
            "password": self._password,
            "questionid": "0",
            "answer": "",
        }

        response = self.session.post(url=url, params=params, data=data)

        html_text = response.text

        if "欢迎您回来" in html_text:
            return True
        else:
            return False

    def build_base_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
            "Accept": "application/json;charset=UTF-8"
        }

    def get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        return "cookie", current_user_config_data["cookie"], True

    def check_expire_task_run(self) -> bool:
        """
        检查cookie是否过期
        :return: cookie过期返回True，cookie未过期返回False
        """
        # 积分商城页面
        url = "https://bbs.binmt.cc/keke_integralmall-keke_integralmall.html"
        response = self.session.get(url=url)
        # 判断是否存在"买家中心"，存在则表示cookie未过期
        if "买家中心" in response.text:
            return False
        else:
            return True

    def sign_task_run(self, *args, **kwargs) -> bool:
        url = "https://bbs.binmt.cc/k_misign-sign.html"
        params = {
            "operation": "qiandao",
            "format": "button",
            "formhash": self.__fetch_sign_hash_value(),
            "inajax": "1",
            "ajaxtarget": "midaben_sign"
        }
        response = self.session.get(url=url, params=params)
        if "今日已签" in response.text:
            self.push_msg(f"今日已签到")
            return True
        elif "签到成功" in response.text:
            # 连续签到
            continue_sign = re.search(r'连续(\d+)天', response.text).group(1)
            # 总签到
            total_sign = re.search(r'累计签到.?(\d+).?天', response.text).group(1)
            # 签到奖励
            sign_reward = re.search(r'奖励.?(\d+).?金币', response.text).group(1)
            self.push_msg(
                f"签到成功，奖励{sign_reward}金币，连续签到{continue_sign}天，总签到{total_sign}天")
            return True
        else:
            self.push_msg(f"可能签到失败，原因：{response.text}")
            return False

    def other_task_run(self, *args, **kwargs):
        """
        其他的任务执行入口，默认执行签到任务（无需再次添加，只需要实现了_sign方法即可）
        :return:
        """
        pass

    def last_task_run(self, *args, **kwargs):
        pass

    def __fetch_hash(self, html_text: str, regex: str = r'name="formhash" value="(.*?)"'):
        """
        从源代码中提取hash值
        :param html_text: 源代码
        :param regex: 正则表达式，默认提取formhash
        :return:
        """
        search_result = re.search(regex, html_text)
        if search_result is None:
            raise AttributeError("没有从源代码中找到hash值")
        return search_result.group(1)

    def __fetch_sign_hash_value(self):
        """
        提取签到所需的formhash
        :return:
        """
        url = "https://bbs.binmt.cc/k_misign-sign.html"
        response = self.session.get(url=url)
        return self.__fetch_hash(response.text)

    def __fetch_login_hash_value(self):
        """
        提取登录所需的hash数据（loginhash, formhash）
        :return:
        """
        url = "https://bbs.binmt.cc/member.php"

        params = {
            "mod": "logging",
            "action": "login",
            "infloat": "yes",
            "handlekey": "login",
            "inajax": "1",
            "ajaxtarget": "fwin_content_login"
        }
        response = self.session.get(url=url, params=params)
        formhash = self.__fetch_hash(response.text)
        loginhash = self.__fetch_hash(response.text, regex=r'loginhash=(.*?)">')
        return formhash, loginhash
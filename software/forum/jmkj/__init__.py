# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""
import threading
from typing import Tuple

import config
from common.base_config import BaseUserConfig
from common.base import BaseFileStorageTemplateForAccount


class JMKJ(BaseFileStorageTemplateForAccount):
    JMKJ_DEFAULT_USER_CONFIG = config.DefaultUserConfig.JMKJConfig
    TAG = JMKJ_DEFAULT_USER_CONFIG.tag

    def __init__(self, userConfig: BaseUserConfig = JMKJ_DEFAULT_USER_CONFIG):
        self.__exp_add = 0
        self.__semaphore = threading.BoundedSemaphore(3)
        self.__lock = threading.Lock()
        super().__init__(
            userConfig,
            "jmkj_userinfo"
        )

    def fetch_primary_data(self, username: str, password: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        url = "http://bbs.bbs.jvjyun.com/api/login"
        data = {
            "user": self._username,
            "pass": self._password,
            "sbid": "4a107af0-c599-3858-a9fa-8689c2da2c43"
        }
        response = self.session.post(url=url, data=data)
        try:
            res_json = response.json()
            if "登录成功" not in response.text:
                raise AttributeError(f"登录失败, {res_json['msg']}")
            return True
        except:
            raise AttributeError(f"登录失败")

    def build_base_headers(self) -> dict:
        return {
            "User-Agent": "Apache-HttpClient/UNAVAILABLE (java 1.4)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "bbs.bbs.jvjyun.com",
        }

    def get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        return "cookie", current_user_config_data["cookie"], True

    def check_expire_task_run(self) -> bool:
        """
        检查cookie是否过期
        :return: cookie过期返回True，cookie未过期返回False
        """
        url = "http://bbs.bbs.jvjyun.com/"

        params = {
            "s": "Friend/friend_list"
        }

        data = {
            "user": ""
        }
        response = self.session.post(url=url, params=params, data=data)

        try:
            res_json = response.json()
            if not res_json.get("error", True):
                info = res_json.get("info")
                if "重新登录" in info:
                    return True
                else:
                    self.push_msg(info)
            return False
        except:
            return False

    def sign_task_run(self, *args, **kwargs) -> bool:
        return self.__forum_sign() == self.__homepage_sign()

    def other_task_run(self, *args, **kwargs) -> bool:
        pass

    def last_task_run(self, *args, **kwargs):
        pass

    def __get_forum_id_list(self) -> list:
        """
        获取所有版块ID
        :return:
        """
        url = "http://bbs.bbs.jvjyun.com/api/forum"
        response = self.session.get(url=url)
        try:
            res_json = response.json()
            if forum_list := res_json.get("forumlist"):
                self.push_msg("获取所有版块ID成功!")
                return [forum["id"] for forum in forum_list]
            else:
                raise AttributeError("获取版块ID失败")
        except:
            raise AttributeError("获取版块ID失败")

    def __forum_sign_thread(self, url, forum_id):
        data = {
            "fid": forum_id
        }
        response = self.session.post(url=url, data=data)
        try:
            res_json = response.json()
            if message := res_json.get("message"):
                if str(message).rfind("+") != -1:
                    self.__lock.acquire()
                    # 截取增加的经验值
                    self.__exp_add += int(message[-1])
                    self.__lock.release()
        except:
            self.push_msg(f"版块ID：{forum_id}，签到失败")
        finally:
            self.__semaphore.release()

    def __forum_sign(self):
        forum_list = self.__get_forum_id_list()

        url = "http://bbs.bbs.jvjyun.com/api/bksign"

        for forum_id in forum_list:
            self.__semaphore.acquire()
            threading.Thread(target=self.__forum_sign_thread, args=(url, forum_id)).start()

        self.push_msg(f"版块签到完成，共增加经验：{self.__exp_add}")
        return True

    def __homepage_sign(self):
        """
        主页签到
        :return:
        """
        url = "http://bbs.bbs.jvjyun.com/?plugins/sign.html"
        response = self.session.post(url=url)
        try:
            res_json = response.json()
            info = res_json.get("info")  # 签到信息
            leiji = res_json.get("leiji")  # 累计签到天数
            lianxu = res_json.get("lianxu")  # 连续签到天数

            if res_json.get("err") == 0 and "签到成功" in info:
                self.push_msg(f"主页签到成功, 累计签到{leiji}天，连续签到{lianxu}天")
            else:
                self.push_msg(f"主页签到失败, {info}, 累计签到{leiji}天，连续签到{lianxu}天")
            return True
        except:
            self.push_msg(f"主页签到失败, {response.text}")
            return False

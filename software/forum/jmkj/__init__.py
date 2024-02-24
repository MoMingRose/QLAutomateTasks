# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""
import os
import threading

import config
from common.base import LoginAndSignTemplate
from common.base_config import BaseUserConfig


class JMKJ(LoginAndSignTemplate):
    JMKJ_DEFAULT_USER_CONFIG = config.DefaultUserConfig.JMKJConfig
    TAG = JMKJ_DEFAULT_USER_CONFIG.tag

    def __init__(self, userConfig: BaseUserConfig = JMKJ_DEFAULT_USER_CONFIG):
        self.__exp_add = 0
        self.__semaphore = threading.BoundedSemaphore(3)
        self.__lock = threading.Lock()
        super().__init__(
            userConfig,
            "jiemo_userinfo"
        )

    def _set_files_dir(self):
        return os.path.dirname(__file__)

    def _check_expire(self) -> bool:
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
        response = self.session.post(url=url, params=params, data=data, headers=self._base_headers)

        try:
            res_json = response.json()
            if not res_json.get("error", True):
                info = res_json.get("info")
                if "重新登录" in info:
                    return True
                else:
                    self.print(info)
            return False
        except:
            return False

    def __get_forum_id_list(self) -> list:
        """
        获取所有版块ID
        :return:
        """
        url = "http://bbs.bbs.jvjyun.com/api/forum"
        response = self.session.get(url=url, headers=self._base_headers)
        try:
            res_json = response.json()
            if forum_list := res_json.get("forumlist"):
                self.print("获取所有版块ID成功!")
                return [forum["id"] for forum in forum_list]
            else:
                raise AttributeError("获取版块ID失败")
        except:
            raise AttributeError("获取版块ID失败")

    def __forum_sign_thread(self, url, forum_id):
        data = {
            "fid": forum_id
        }
        response = self.session.post(url=url, data=data, headers=self._base_headers)
        try:
            res_json = response.json()
            if message := res_json.get("message"):
                if str(message).rfind("+") != -1:
                    self.__lock.acquire()
                    # 截取增加的经验值
                    self.__exp_add += int(message[-1])
                    self.__lock.release()
        except:
            self.print(f"版块ID：{forum_id}，签到失败")
        finally:
            self.__semaphore.release()

    def __forum_sign(self):
        forum_list = self.__get_forum_id_list()

        url = "http://bbs.bbs.jvjyun.com/api/bksign"

        for forum_id in forum_list:
            self.__semaphore.acquire()
            threading.Thread(target=self.__forum_sign_thread, args=(url, forum_id)).start()

        self.print(f"{self._username}，版块签到完成，共增加经验：{self.__exp_add}")
        return True

    def __homepage_sign(self):
        """
        主页签到
        :return:
        """
        url = "http://bbs.bbs.jvjyun.com/?plugins/sign.html"
        response = self.session.post(url=url, headers=self._base_headers)
        try:
            res_json = response.json()
            info = res_json.get("info")  # 签到信息
            leiji = res_json.get("leiji")  # 累计签到天数
            lianxu = res_json.get("lianxu")  # 连续签到天数

            if res_json.get("err") == 0 and "签到成功" in info:
                self.print(f"{self._username}，主页签到成功, 累计签到{leiji}天，连续签到{lianxu}天")
            else:
                self.print(f"{self._username}，主页签到失败, {info}, 累计签到{leiji}天，连续签到{lianxu}天")
            return True
        except:
            self.print(f"{self._username}，主页签到失败, {response.text}")
            return False

    def _sign(self):
        # 版块、主页签到
        return self.__forum_sign() == self.__homepage_sign()

    def _login(self):
        url = "http://bbs.bbs.jvjyun.com/api/login"
        data = {
            "user": self._username,
            "pass": self._password,
            "sbid": "4a107af0-c599-3858-a9fa-8689c2da2c43"
        }
        response = self.session.post(url=url, data=data, headers=self._base_headers)
        try:
            res_json = response.json()
            if "登录成功" not in response.text:
                raise AttributeError(f"{self._username}登录失败, {res_json['msg']}")
            return True
        except:
            raise AttributeError(f"{self._username}登录失败")

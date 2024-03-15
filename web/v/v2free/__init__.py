# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 25/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-25
【功能描述】
"""
import os
import re
import time
from typing import Tuple

import requests

import config
from common.base import BaseFSTemplateForAccount
from common.base_config import BaseTaskConfig


class V2Free(BaseFSTemplateForAccount):
    V2FREE_DEFAULT_USER_CONFIG = config.DefaultTaskConfig.V2FreeConfig
    TAG = V2FREE_DEFAULT_USER_CONFIG.task_name

    def __init__(self, taskConfig: BaseTaskConfig = V2FREE_DEFAULT_USER_CONFIG):
        self.data_sitekey: str = ""
        super().__init__(taskConfig, "v2free_userinfo")

    def build_base_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
            "Accept": "application/json;charset=UTF-8"
        }

    def get_homepage(self) -> str | None:
        url = "https://w1.v2free.top/user/"
        response = self.session.get(url=url)
        try:
            return response.text
        except:
            pass

    def fetch_primary_data(self, username: str, password: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        url = "https://w1.v2free.top/auth/login"
        data = {
            "email": username,
            "passwd": password,
            "code": "",
            "remember_me": "week",  # 勾选“记住我”复选框会出现此参数，应该是用来设置cookie过期时间的，勾选后cookie过期时间会更长一点
        }
        response = self.session.post(url=url, data=data)
        # 获取登录后的响应
        try:
            res_json = response.json()
            if res_json["ret"] == 1 and res_json["msg"] == "登录成功":
                return True
            else:
                self.push_msg(f"登录失败", res_json.get("msg", response.text))
                return False
        except:
            self.push_msg(f"登录失败", response.text)
            return False

    def get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        # 这里的主要数据是cookie
        return "cookie", current_user_config_data["cookie"], False

    def check_expire_task_run(self) -> bool:
        """
        检查cookie是否过期
        :return: cookie过期返回True，cookie未过期返回False
        """
        html = self.get_homepage()
        if html and "用户中心" not in html:
            return True

        # 通过正则表达式获取data-sitekey
        self.data_sitekey = self.__fetch_data_sitekey(html)
        return False

    def sign_task_run(self, *args, **kwargs) -> bool:
        if self.data_sitekey == "":
            # 通过正则表达式获取data-sitekey
            self.data_sitekey = self.__fetch_data_sitekey()

        url = "https://w1.v2free.top/user/checkin"
        data = {
            "recaptcha": self.pass_captchaV2(),
        }
        response = self.session.post(url=url, data=data)
        try:
            res_json = response.json()
            msg = res_json["msg"]  # 签到成功并获取了多少流量
            if res_json["ret"] == 1:
                traffic = res_json["traffic"]  # 当前总流量
                self.push_msg(f"签到成功, {msg}, 当前总流量: {traffic}")
                return True
            else:
                self.push_msg(f"签到失败, {msg}")
                return False
        except:
            self.push_msg(f"签到失败", response.text)
            return False

    def other_task_run(self, *args, **kwargs):
        """
        其他的任务执行入口，默认执行签到任务（无需再次添加，只需要实现了_sign方法即可）
        :return:
        """
        pass

    def last_task_run(self, *args, **kwargs):
        pass

    def pass_captchaV2(self):
        """
        自定义通过验证码的方法

        :return: result : string 验证码识别结果
        """

        client_key = os.environ.get("YESCAPTCHA_CLIENTKEY")

        if client_key is None:
            raise Exception(
                "请设置 “YESCAPTCHA_CLIENTKEY” 环境变量!\n通过下方【邀请链接】注册后，首页显示的就是clientKey\nhttps://yescaptcha.com/i/jFtvBe")

        # 这里选择使用https://yescaptcha.com/i/jFtvBe提供的接口
        # 1. 创建识别任务
        taskId = self.create_task(client_key)
        if taskId is None:
            raise Exception("识别任务创建失败!")
        else:
            self.push_msg("识别任务创建成功!", taskId)

        # 2. 获取识别结果
        result = self.get_response(client_key, taskId)
        if result is None:
            raise Exception("获取识别结果失败")

        return result

    def create_task(self, client_key: str) -> str:
        """
        第一步，创建验证码任务
        :param
        :return taskId : string 创建成功的任务ID
        """

        url = "https://api.yescaptcha.com/createTask"
        data = {
            "clientKey": client_key,
            "task": {
                "websiteURL": "https://v2free.net/user",
                "websiteKey": self.data_sitekey,
                "type": "NoCaptchaTaskProxyless"
            }
        }
        try:
            self.push_msg("开始创建识别任务...", is_push=False)
            # 发送JSON格式的数据
            result = requests.post(url, json=data).json()
            taskId = result.get('taskId')
            if taskId is not None:
                return taskId
        except Exception as e:
            raise Exception(f"创建识别任务失败: {e}")

    def get_response(self, client_key: str, taskID: str):
        """
        第二步：使用taskId获取response
        :param taskID: string
        :return response: string 识别结果
        """
        self.push_msg("开始获取识别结果,每3秒请求一次，请耐心等待...", is_push=False)
        # 循环请求识别结果，3秒请求一次
        times = 0
        while times < 120:
            try:
                url = f"https://api.yescaptcha.com/getTaskResult"
                data = {
                    "clientKey": client_key,
                    "taskId": taskID
                }
                # res_json = requests.post(url, json=data, verify=False).json()
                res_json = requests.post(url, json=data).json()
                if res_json.get("errorId") == 0:
                    if res_json.get("status") == "ready":
                        self.push_msg("识别任务已完成，正在获取识别结果...", is_push=False)
                        if solution := res_json.get('solution', {}):
                            response = solution.get('gRecaptchaResponse')
                            if response:
                                self.push_msg("识别结果获取成功!", is_push=False)
                                return response
                            else:
                                self.push_msg("识别结果获取失败!", is_push=False)
                                return None
                        else:
                            raise Exception("识别结果获取失败!")
                    else:
                        self.push_msg("识别任务还在进行中，继续请求中...", is_push=False)
                else:
                    self.push_msg("❌ 识别任务失败! ",
                                  f"错误id：{res_json.get('errorId')} \n错误代码: {res_json.get('errorCode')} \n错误描述: {res_json.get('errorDescription')}",
                                  "请前往https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/5603341/errorCode查看详细错误原因",
                                  sep="\n")
            except Exception as e:
                raise Exception(f"获取识别结果失败: {e}")
            times += 3
            time.sleep(3)

    def __fetch_data_sitekey(self, html=None):
        """
        获取 data-sitekey
        :param html:
        :return:
        """
        if html is None:
            html = self.get_homepage()
        try:
            # 使用正则提取
            return re.findall(r'data-sitekey="(.+?)"', html)[0]
        except:
            raise AttributeError("获取 data-sitekey 失败，今日签到任务或许已经完成!")

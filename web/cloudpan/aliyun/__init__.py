# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""
import os

import config
from common.base import TokenTemplate
from common.base_config import BaseTokenConfig


class AL(TokenTemplate):
    AL_DEFAULT_USER_CONFIG = config.DefaultUserConfig.ALYPConfig
    TAG = AL_DEFAULT_USER_CONFIG.tag

    def __init__(self, userConfig: BaseTokenConfig = AL_DEFAULT_USER_CONFIG):
        super().__init__(
            userConfig,
            "alyp_userinfo"
        )

    def _get_access_token(self):
        url = 'https://auth.aliyundrive.com/v2/account/token'
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._token
        }
        response = self.session.post(url, json=data)
        try:
            access_token = response.json()["access_token"]
            if access_token:
                self.local_user_config["Authorization"] = f"Bearer {access_token}"
                self.flash_config(self.local_user_config_path)
                self.session.headers.update({"Authorization": f"Bearer {access_token}"})
                return access_token
        except Exception as e:
            self.print(response.text)

    def __request_reward(self, sign_day: int):
        url = 'https://member.aliyundrive.com/v1/activity/sign_in_reward'
        response = self.session.post(
            url,
            params={"_rx-s": "mobile"},
            json={'signInDay': sign_day}
        )
        try:
            res_json = response.json()
            # TODO: 待验证程序的完整性（响应数据以及print打印是否正确）
            if not res_json['success']:
                return False
            reward = res_json['result']
            self.print(
                f"第{sign_day}天签到奖励领取成功, 获得{reward['name']}, {reward['description']}, {reward['notice']}, {reward['subNotice']}")
        except Exception as e:
            self.print(response.text)
            self.print(e)
            return False

    def __request_sign_in_list(self):
        """
        请求签到列表
        :return:
        """
        url = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
        response = self.session.post(
            url,
            params={"_rx-s": "mobile"},
            json={"isReward": False}
        )
        try:
            res_json = response.json()
            if res_json.get("success"):
                res_json = res_json.get("result")
                signInCount = res_json.get("signInCount")  # 本月累计签到天数
                signInLogs = res_json.get("signInLogs")  # 签到日志列表
                lastSignInLog = signInLogs[signInCount - 1]  # 最近一次的签到日志
                # 从签到日志列表中提取出允许领取奖励的任务
                rewardList = [log for log in signInLogs if log.get("status") == "normal" and not log.get("isReward")]
                # 判断是否存在未领取奖励的签到任务
                if rewardList:
                    # 如果存在，则领取所有未领取的奖励
                    for reward in rewardList:
                        # 获取待领取的天数
                        day = reward.get("day")
                        # 发起请求，领取指定天数的奖励
                        self.__request_reward(day)
                else:
                    reward = lastSignInLog.get("reward")
                    reward_name = reward.get("name")
                    reward_desc = reward.get("description")
                    reward_notice = reward.get("notice")
                    reward_subNotice = reward.get("subNotice")
                    self.print(
                        f"今日已签到, 本月累计签到天数: {signInCount}, 今天签到日志: {reward_name}, {reward_desc}, {reward_notice}, {reward_subNotice}")

                return True
            elif res_json.get("message") == "not login":
                self.print("accessToken已经失效，重新获取中...")
                self._get_access_token()
                return self.__request_sign_in_list()
            return True
        except Exception as e:
            self.print(response.text)
            self.print(e)
            return False

    def _sign(self):
        # self._get_access_token()
        return self.__request_sign_in_list()

    def other_task_run(self):
        pass

    def last_task_run(self):
        pass

    def _set_files_dir(self):
        return os.path.dirname(__file__)

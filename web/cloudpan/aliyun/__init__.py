# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""
from typing import Tuple

import config
from common.base_config import BaseUserConfig
from common.base import BaseFileStorageTemplateForToken


class AL(BaseFileStorageTemplateForToken):
    AL_DEFAULT_USER_CONFIG = config.DefaultUserConfig.ALYPConfig
    TAG = AL_DEFAULT_USER_CONFIG.tag

    def __init__(self, userConfig: BaseUserConfig = AL_DEFAULT_USER_CONFIG):
        super().__init__(
            userConfig,
            "alyp_userinfo"
        )

    def fetch_primary_data(self, nickname: str, token: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        """
        这里通过阿里云盘的refresh_token来获取access_token
        :param nickname: 
        :param token: refresh_token
        :param args: 
        :param kwargs: 
        :return: 
        """

        access_token = self.__request_assess_token(refresh_token=token)
        if access_token:
            return "Authorization", f"Bearer {access_token}", True
        return False

    def get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        return "Authorization", current_user_config_data["Authorization"], True

    def sign_task_run(self, nickname: str, token: str, *args, **kwargs) -> bool:
        """
        签到任务
        :param nickname: 昵称
        :param token: refresh_token
        :param args:
        :param kwargs:
        :return:
        """
        res_json = self.__request_sign_list()
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
                self.push_msg(
                    f"今日已签到, 本月累计签到天数: {signInCount}, 今天签到日志: {reward_name}, {reward_desc}, {reward_notice}, {reward_subNotice}")

            return True
        elif res_json.get("message") == "not login":
            self.push_msg("accessToken已经失效，重新获取中...")
            self.fetch_primary_data(*args, **kwargs)
            return self.sign_task_run(*args, **kwargs)
        return True

    def build_base_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
            "Accept": "application/json;charset=UTF-8"
        }

    def check_token_is_expire(self, token: str) -> bool:
        """
        检查阿里云盘的refresh_token是否过期
        :param token:
        :return:
        """
        # 获取access_token
        access_token = self.__request_assess_token(refresh_token=token)
        # 判断是否获取成功
        if access_token:
            # 能刷新，则表示未过期，返回False
            return False
        return True

    def __request_assess_token(self, refresh_token: str) -> str | None:
        """
        通过refresh_token刷新access_token
        :param refresh_token:
        :return:
        """
        url = 'https://auth.aliyundrive.com/v2/account/token'
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        response = self.session.post(url, json=data)
        try:
            access_token = response.json()["access_token"]
            if access_token:
                # 保存access_token
                self.current_user_config_data["Authorization"] = f"Bearer {access_token}"
                self.flash_current_user_config_data()
                return access_token
        except Exception as e:
            self.push_msg(response.text, is_push=False)
            self.push_msg(e, is_push=False)

    def __request_sign_list(self) -> dict | None:
        """
        获取签到列表（通过access_token）
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
            return res_json
        except Exception as e:
            self.push_msg(response.text, is_push=False)
            self.push_msg(e, is_push=False)

    def __request_reward(self, sign_day: int):
        """
        领取奖励（通过access_token）
        :param sign_day: 要领取奖励的天数
        :return:
        """
        url = 'https://member.aliyundrive.com/v1/activity/sign_in_reward'
        response = self.session.post(
            url,
            params={"_rx-s": "mobile"},
            json={'signInDay': sign_day}
        )
        try:
            res_json = response.json()
            if not res_json['success']:
                return False
            reward = res_json['result']
            self.push_msg(
                f"第{sign_day}天签到奖励领取成功, 获得{reward['name']}, {reward['description']}, {reward['notice']}, {reward['subNotice']}")
        except Exception as e:
            self.push_msg(response.text)
            self.push_msg(e)
            return False

    def other_task_run(self, *args, **kwargs) -> bool:
        pass

    def last_task_run(self, *args, **kwargs):
        pass

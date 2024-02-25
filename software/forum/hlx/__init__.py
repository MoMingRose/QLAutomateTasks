# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 23/2/2024.
"""
【作者】MoMingLog
【创建时间】2024-02-23
【功能描述】
"""
import time
from typing import Tuple

import config
from common.base_config import BaseUserConfig
from common.base import BaseFileStorageTemplateForAccount
from utils import crypt_utils


class HLX(BaseFileStorageTemplateForAccount):
    HLX_DEFAULT_USER_CONFIG = config.DefaultUserConfig.HLXConfig
    TAG = HLX_DEFAULT_USER_CONFIG.tag
    STATIONARY_CODE = "fa1c28a5b62e79c3e63d9030b6142e4b"
    DEVICE_CODE = "[d]a87e1f0e-32d5-4331-bc12-4a41925f4eb5"

    def __init__(self, userConfig: BaseUserConfig = HLX_DEFAULT_USER_CONFIG):
        self._key = None
        self.__hash_pwd = None
        self.cate_ids = {}
        super().__init__(
            userConfig,
            "hlx_userinfo"
        )

    def fetch_primary_data(self, username: str, password: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        url = "http://floor.huluxia.com/account/login/ANDROID/4.1.8"

        params = self.__build_params()
        self.__hash_pwd = crypt_utils.md5(password)
        data = {
            "account": username,
            "login_type": 2,
            "password": self.__hash_pwd,
            "sign": self.__calculate_sign_for_login()
        }

        response = self.session.post(url=url, params=params, data=data)

        try:
            res_json = response.json()
            res_status = res_json['status']
            if res_status == 1:
                _key = res_json['_key']  # 获取登录后的_key值，这个可以用来进行后续的操作
                self.current_user_config_data["_key"] = _key
                self.flash_current_user_config_data()
                return True
        except Exception as e:
            self.push_msg(e)

    def build_base_headers(self) -> dict:
        return {
            "User-Agent": "okhttp/3.8.1",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "floor.huluxia.com"
        }

    def get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        return "_key", current_user_config_data["_key"], False

    def check_expire_task_run(self) -> bool:
        url = "http://floor.huluxia.com/account/security/info/ANDROID/4.2.2"
        params = self.__build_params(self.current_user_config_data.get("_key"))
        response = self.session.get(url, params=params)
        try:
            res_json = response.json()
            if res_json.get("code") == 103 and res_json.get("msg") == "未登录":
                return True
            self.cate_ids = self.__request_cate_id_list()
            return False
        except Exception as e:
            return True

    def sign_task_run(self, *args, **kwargs) -> bool:
        url = "http://floor.huluxia.com/user/signin/ANDROID/4.1.8"
        if len(self.cate_ids.keys()) == 0:
            self.cate_ids = self.__request_cate_id_list()
        cate_ids_len = len(self.cate_ids.keys())
        sum_exp = 0
        sum_sign_count = 0

        for cate_id, cate_title in self.cate_ids.items():

            params = self.__build_params(self.current_user_config_data.get("_key"))
            time_str = int(time.time() * 1000)
            params.update({
                "cat_id": cate_id,
                "time": time_str,
            })

            response = self.session.post(
                url,
                params=params,
                data={
                    "sign": self.__calculate_sign_for_signIn(cate_id, time_str)
                }
            )
            try:
                res_json = response.json()
                if res_json['signin'] == 1:
                    continueDays = res_json['continueDays']  # 连续签到天数
                    experienceVal = res_json['experienceVal']  # 获取经验点数
                    nextExperience = res_json['nextExperience']  # 下一次签到获取的经验点数
                    sum_exp += experienceVal
                    sum_sign_count += 1
                    self.push_msg(
                        f'{cate_title} 连续签到{continueDays}天，获得{experienceVal}点经验，下阶段签到可获得{nextExperience}经验',
                        is_push=False)
                else:
                    self.push_msg(f"{cate_title}，签到失败")
            except Exception as e:
                self.push_msg(f"{cate_title}，签到失败")
        if sum_exp > 0:
            self.push_msg(f"签到成功！经验增加点数：{sum_exp} 版块签到个数: {sum_sign_count} 总版块个数：{cate_ids_len}")
        return True

    def other_task_run(self, *args, **kwargs) -> bool:
        pass

    def last_task_run(self, *args, **kwargs):
        pass

    def __build_params(self, _key=""):
        """
        构造参数值
        :param _key:
        :return:
        """
        return {
            "platform": 2,
            "gkey": "000000",
            "app_version": "4.3.0.2",
            "versioncode": "20141492",
            "market_id": "floor_tencent",
            "_key": _key,
            "device_code": self.DEVICE_CODE,
            "phone_brand_": "MI",
            "hlx_imei": "",
            "hlx_android_id": "c9f6420541ab2b2a",
            "hlx_oaid": "5722f7892e40e10e"
        }

    def __calculate_sign_for_signIn(self, cate_id: int, time_str: int):
        """
        计算版块签到要用到的sian值
        :param cate_id:
        :param time_str:
        :return:
        """
        return crypt_utils.md5(
            f"cat_id{cate_id}time{time_str}{self.STATIONARY_CODE}"
        )

    def __calculate_sign_for_login(self):
        """
        计算登录用到的sign值
        :return:
        """
        return crypt_utils.md5(
            f"account{self._username}device_code{self.DEVICE_CODE}password{self.__hash_pwd}voice_code{self.STATIONARY_CODE}"
        )

    def __request_cate_id_list(self) -> dict:
        """
        请求版块ID列表
        :return:
        """
        url = "http://floor.huluxia.com/category/list/ANDROID/4.2.3"
        params = self.__build_params()
        response = self.session.get(url, params=params.update({
            "is_hidden": 1,
            "is_recommended": 1
        }))
        try:
            res_json = response.json()
            if res_json.get("status") == 1:
                categories = res_json.get("categories")
                return {cate.get("categoryID"): cate.get("title") for cate in categories if
                        cate.get("categoryID") != 0}
            else:
                return {}
        except Exception as e:
            return {}
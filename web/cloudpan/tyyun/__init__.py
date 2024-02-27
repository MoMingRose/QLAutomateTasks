# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 12/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-12
【功能描述】 天翼云盘自动任务
"""
import base64
import json
import os
import re
import time
from typing import Tuple

import requests
import ujson

import config
from common.base import BaseFileStorageTemplateForAccount
from common.base_config import BaseUserConfig
from utils.crypt_utils import rsa_encrypt, aes_encrypt, aes_decrypt
from utils.generator_utils import uuid_generator, rates_generator
from utils.ocr_utils import slide_match
from web.cloudpan.tyyun.scheme import *


class TY(BaseFileStorageTemplateForAccount):
    TY_DEFAULT_USER_CONFIG = config.DefaultUserConfig.TYYPConfig
    TAG = TY_DEFAULT_USER_CONFIG.tag

    def __init__(self, userConfig: BaseUserConfig = TY_DEFAULT_USER_CONFIG):
        # appConf.do 相关响应数据
        self.__app_conf_res_data: AppConfig
        # encryptConf.do 相关响应数据
        self.__encrypt_conf_res_data: EncryptConfig
        # 验证码检验通过的数据
        self.__pass_captcha_data: PassCaptchaData = PassCaptchaData()

        super().__init__(
            userConfig,
            default_env_key="tyyp_userinfo"
        )

    def fetch_primary_data(self, username: str, password: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        try:
            self.__prepare_for_login()
        except ImportError as e:
            self.push_msg(e)
            return False

        self.push_msg("正在准备登录...", is_push=False)
        # 登录前期准备工作
        # 登录链接
        login_url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
        # 构造请求体
        data = {
            "version": "v2.0",
            "apToken": "",
            "appKey": self.__app_conf_res_data.appKey,
            "accountType": self.__app_conf_res_data.accountType,
            "userName": f"{self.__encrypt_conf_res_data.pre}{self.__rsa_encrypt_for_login(self._username)}",
            "epd": f"{self.__encrypt_conf_res_data.pre}{self.__rsa_encrypt_for_login(self._password)}",
            "captchaType": self.__pass_captcha_data.captchaType,
            "validateCode": self.__pass_captcha_data.validate,
            "smsValidateCode": self.__pass_captcha_data.validate,
            "captchaToken": self.__pass_captcha_data.token,
            "returnUrl": self.__app_conf_res_data.returnUrl,
            "mailSuffix": self.__app_conf_res_data.mailSuffix,
            "dynamicCheck": "FALSE",
            "clientType": self.__app_conf_res_data.clientType,
            "cb_SaveName": 0,
            "isOauth2": self.__app_conf_res_data.isOauth2,
            "state": "",
            "paramId": self.__app_conf_res_data.paramId
        }

        response = self.session.post(login_url, data=data)
        res_json = response.json()
        msg = res_json.get("msg")
        if msg in ["密码不正确", "账户名或密码错误"]:
            raise Exception("登录失败! 账户名或密码错误!")
        elif msg == "登录成功":
            # 获取重定向链接（主要是为了更新代表用户的cookie）
            toUrl = res_json.get("toUrl")
            # 发送重定向请求
            self.session.get(toUrl)
            return True
        else:
            raise Exception(" 登录失败" + ujson.dumps(res_json))

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
        :return: 过期返回True，否则返回False
        """
        userinfo = self._get_userinfo()
        try:
            if userinfo is not None and userinfo["res_message"] == "成功":
                return False
            return True
        except Exception as e:
            self.push_msg("检查cookie是否过期任务执行异常，原因：", e, is_push=False)
            return True

    def sign_task_run(self, *args, **kwargs) -> bool:
        sign_url = "https://m.cloud.189.cn/mkt/userSign.action"

        response = self.session.get(sign_url)
        try:
            res_json = response.json()
            bonus = res_json.get('netdiskBonus')
            if res_json.get("isSign"):
                self.push_msg(f"请勿重复签到, 今日已经获得签到奖励: {bonus}M空间")
            else:
                self.push_msg(f"签到成功, 获得签到奖励: {bonus}")
            return True
        except Exception as e:
            self.push_msg(f"签到异常, 原因：{e}")
            return False

    def other_task_run(self, *args, **kwargs) -> bool:
        """
        其他的任务执行入口，默认执行签到任务（无需再次添加，只需要实现了_sign方法即可）
        :return:
        """
        ret = []

        if self.check_run_task_permission("lucky"):
            # 抽奖任务
            if self.__lucky_task_run():
                self.lock_task("lucky")
                ret.append(True)
        else:
            self.push_msg("今日抽奖任务已完成!")

        return all(ret)

    def last_task_run(self, *args, **kwargs):
        # 打印用户信息任务（方便统计）
        self._print_userinfo()

    def __lucky_task_run(self):
        """
        抽奖
        :return:
        """
        lucky_urls = [
            "https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN",
            "https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN",
            "https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_2022_FLDFS_KJ&activityId=ACT_SIGNIN"
        ]

        lucky_index = 0

        ret = []

        for lucky_url in lucky_urls:
            lucky_index += 1
            response = self.session.get(lucky_url)
            try:
                res_json = response.json()
                if res_json.get("errorCode"):
                    self.push_msg(f"抽奖序号: {lucky_index} 请勿重复抽奖, 今日已经抽奖")
                else:
                    self.push_msg(f"抽奖序号: {lucky_index} 抽奖成功, 获得抽奖奖励: {res_json.get('description')}")
                ret.append(True)
            except Exception as e:
                self.push_msg(f"抽奖序号: {lucky_index} 抽奖异常, 原因：{e}")
                ret.append(False)
        return all(ret)

    def _print_userinfo(self):
        userinfo = self._get_userinfo()
        if userinfo is not None and userinfo["res_message"] == "成功":
            userinfo = UserInfoData.model_validate(userinfo)
            self.push_msg(
                f"用户空间容量：\n可用{round(userinfo.available / 1073741824, 2)} GB\n总共{round(userinfo.capacity / 1073741824, 2)} GB")
        else:
            self.push_msg("获取用户信息失败")

    def _get_userinfo(self):
        """
        获取用户信息
        :return:
        """
        url = "https://cloud.189.cn/api/open/user/getUserInfoForPortal.action"

        response = self.session.get(url, headers=self.base_headers)

        try:
            return response.json()
        except:
            self.push_msg(response.text)
            return None

    def __prepare_for_login(self):
        """
        登录前期准备工作（登录参数获取）
        :return:
        """
        # 提取第一次重定向链接，含：unifyAccountLogin.do，
        first_redirect_url = self.__fetch_redirect_url(
            "https://cloud.189.cn/api/portal/loginUrl.action?redirectURL=https://cloud.189.cn/web/redirect.html")
        # 提取第二次重定向链接，这次链接中包含登录请求头中的必要参数, lt, reqId
        # 此外，此链接本身就是请求头中的Referer
        second_redirect_url = self.__fetch_redirect_url(first_redirect_url)
        lt = re.findall(r'lt=(\S+)&', second_redirect_url)[0]
        reqId = re.findall(r'reqId=(\S+)', second_redirect_url)[0]
        # 更新会话中的请求头信息
        self.session.headers.update({
            "Referer": second_redirect_url,
            "lt": lt,
            "reqid": reqId,
        })

        # 发送获取配置请求1：appConf.do
        # 此中可以获取到登录请求体中的大部分数据
        app_conf_url = "https://open.e.189.cn/api/logbox/oauth2/appConf.do"

        app_conf_response = self.session.post(app_conf_url, data={
            "version": "2.0",
            "appKey": "cloud"
        })

        self.__app_conf_res_data = AppConfig.model_validate(app_conf_response.json()["data"])

        # 发送获取配置请求2：encryptConf.do
        # 此中可以获取到rsa加密的公钥，以及加密数据的前缀内容
        encrypt_conf_url = "https://open.e.189.cn/api/logbox/config/encryptConf.do"

        encrypt_conf_response = self.session.post(encrypt_conf_url, data={
            "appId": "cloud"
        })

        self.__encrypt_conf_res_data = EncryptConfig.model_validate(encrypt_conf_response.json()["data"])

        # 发送判断是否验证码检测请求：needcaptcha.do
        if self.__check_need_captcha():
            self.push_msg("检测到需要进行滑块拼图验证", is_push=False)
            attempts = 3
            self.push_msg(f"正在尝试（{attempts}次）后台自动破解...", is_push=False)
            for attempt in range(attempts):
                self.push_msg(f"正在尝试第{attempt + 1}次破解...", is_push=False)
                # 获取滑块验证码数据
                captcha_data = CaptchaData.model_validate(self.__get_captcha_data(second_redirect_url).get("data"))
                # 解析滑块验证码
                x = self.__parse_captcha_data(captcha_data)
                # 生成滑动轨迹相关数据
                data = rates_generator(x)
                # 添加一些其它必要数据
                data.update({
                    "token": captcha_data.token,
                    "captchaType": 1,
                    "points": [{"x": x, "y": 0}],
                    "finger": 3942878568
                })
                # 获取UUID并进行Base64编码
                b64_uuid = base64.b64encode(uuid_generator().encode()).decode()
                # 构造请求参数
                params = {
                    # 将data数据进行AES加密
                    "pb": aes_encrypt(json.dumps(data, separators=(',', ':')), b64_uuid),
                    # 将编码后的uuid进行RSA加密
                    "cp": self.__rsa_encrypt_for_captcha(b64_uuid),
                    "appId": "cloud",
                    "version": "1.0.1",
                    "reqId": uuid_generator(32),
                    "callback": "callback"
                }
                # 发送检查验证是否通过请求
                url = "https://open.e.189.cn/gw/captcha/check.do"

                response = self.session.get(url, params=params)
                # 提取json字符串
                callback = re.findall(r'callback\((\S+)\)', response.text)[0]
                # 获取data加密数据
                pass_en_data = json.loads(callback).get("data")
                # 如果验证通过，则会返回加密数据，否则会返回None
                if pass_en_data:
                    self.push_msg("滑块验证码已通过!")
                    self.push_msg("正在解密返回结果...", is_push=False)
                    pass_captcha_data = aes_decrypt(pass_en_data, b64_uuid)
                    self.__pass_captcha_data = PassCaptchaData.model_validate_json(pass_captcha_data)
                    self.push_msg("解密成功!", is_push=False)
                    break
                else:
                    self.push_msg("滑块验证码破解失败!", is_push=False)
            self.clear_captcha_images()

    def __fetch_redirect_url(self, request_url: str):
        """
        提取重定向链接
        :param request_url: 请求链接
        :return: 重定向链接
        """
        # 发送请求，并停止重定向
        response = self.session.get(request_url, headers=self.base_headers, allow_redirects=False)
        # 获取响应头中的重定向链接
        return response.headers["Location"]

    def __check_need_captcha(self):
        """
        判断是否需要验证码
        :return: 需要验证返回True， 否则返回 False
        """
        # 如果需要验证，响应体则会返回1，否则返回0
        captcha_url = "https://open.e.189.cn/api/logbox/oauth2/needcaptcha.do"
        # 构建请求体
        data = {
            "accountType": self.__app_conf_res_data.accountType,
            "userName": f"{self.__encrypt_conf_res_data.pre}{self.__rsa_encrypt_for_login(self._username)}",
            "appKey": self.__app_conf_res_data.appKey
        }
        # 发送请求
        response = self.session.post(captcha_url, headers=self.base_headers, data=data)
        if response.text == "1":
            return True
        return False

    def __get_captcha_data(self, referer_url):
        """
        获取滑块拼图验证码数据
        :param referer_url: 第二次重定向连接
        :return:
        """
        # 将UUID进行base64编码
        b64_uuid = base64.b64encode(uuid_generator().encode()).decode()

        url = "https://open.e.189.cn/gw/captcha/get.do"
        # 构建请求参数
        stamp_time = int(time.time() * 1000)

        # 构造pb原始数据
        ori_data = {
            "appId": "cloud",
            "captchaType": 1,
            "referer": referer_url,
            "time": stamp_time,
            "finger": 3942878568,  # 这里我选择固定，其他情况还未测试过
            "width": "310"
        }

        params = {
            # 将pb原始数据进行AES加密
            "pb": aes_encrypt(ori_data, common_key=b64_uuid),
            # 将编码后的uuid进行RSA加密
            "cp": self.__rsa_encrypt_for_captcha(b64_uuid),
            "appId": "cloud",
            "version": "1.0.1",
            "reqId": uuid_generator(32),
            "callback": f"callback_{stamp_time}"
        }
        # 发送请求
        response = requests.get(url, params=params)
        if "系统异常" in response.text:
            raise Exception("官方系统异常，获取滑块验证码数据失败，请等待官方恢复后再试!")
        # 提取json字符串
        t = re.findall(r'callback_\d+\((\S+)\)', response.text)[0]
        return json.loads(t)

    def __parse_captcha_data(self, captcha_data: CaptchaData) -> int:
        """
        解析滑块验证码（解析出需要移动的距离）
        :return: 返回需要移动的距离
        """
        # 处理滑块验证码图片
        self.__handle_captcha_image(captcha_data)
        # 读取小滑块图片数据
        tg_data = self.__read_target_captcha_image()
        # 读取背景图片数据
        bg_data = self.__read_background_captcha_image()

        # 解析滑块验证码
        parse_result = slide_match(tg_data, bg_data).get("target")
        # 数组中第一个值就是需要移动的x轴距离
        return parse_result[0]

    @property
    def captcha_target_img(self):
        return os.path.join(self.root_dir_path, f"{self.hash_value}_target.png")

    @property
    def captcha_background_img(self):
        return os.path.join(self.root_dir_path, f"{self.hash_value}_background.png")

    def __handle_captcha_image(self, captcha_data: CaptchaData):
        """
        处理滑块验证码图片
        :param captcha_data: 验证码数据
        :return:
        """
        # 分离出小滑块图片和背景图片的base64编码
        target_image_base64 = captcha_data.front.split(",")[1]
        background_image_base64 = captcha_data.bg.split(",")[1]
        # 保存小滑块图片
        self.__save_captcha_image(target_image_base64, self.captcha_target_img)
        # 保存背景图片
        self.__save_captcha_image(background_image_base64, self.captcha_background_img)

    def __read_target_captcha_image(self):
        """
        读取目标图片
        :return:
        """
        with open(self.captcha_target_img, 'rb') as file:
            return file.read()

    def __read_background_captcha_image(self):
        """
        读取背景图片
        :return:
        """
        with open(self.captcha_background_img, 'rb') as file:
            return file.read()

    def __save_captcha_image(self, image_base64, image_path: str):
        """
        保存验证码图片
        :param image_base64: base64编码的图片文本格式
        :param file_name: 保存的文件名
        :return:
        """
        # 去除base64编码中的前缀
        img_data = image_base64.split(';base64,')[-1]

        # 将base64解码为二进制数据
        img_binary = base64.b64decode(img_data)

        # 写入图片文件
        with open(image_path, 'wb') as file:
            file.write(img_binary)

    def clear_captcha_images(self):
        """
        清除验证码图片
        :return:
        """
        if os.path.exists(self.captcha_target_img):
            os.remove(self.captcha_target_img)
        if os.path.exists(self.captcha_background_img):
            os.remove(self.captcha_background_img)

    def __rsa_encrypt_for_captcha(self, data: str):
        """
        使用rsa加密数据，用于验证码
        :param data: 待加密数据
        :return: 加密后的数据
        """
        pubKey = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDky91Sokyr2UI/K87VMiZp/Pmiggg4fFKgclUZoPCoO+FvdeU/wSvv59Z6fEZi4Uvtzzv5UqCMfFRykokoiGSq8B3X1kr24RbtsWif/+pxfRDCA8tXw3V2DIZ/a03tg8BBgQLpdWuwTmM1448WFIs5O9pyFgjKDFoo5cWvs88HBQIDAQAB"
        return rsa_encrypt(data, pubKey)

    def __rsa_encrypt_for_login(self, data: str):
        """
        使用rsa加密数据，用于登录参数
        :param data: 待加密数据
        :return: 加密后的数据
        """
        return rsa_encrypt(data, self.__encrypt_conf_res_data.pubKey)

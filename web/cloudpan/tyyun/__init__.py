# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 12/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-12
【功能描述】
"""
import base64
import json
import os
import re
import time

import requests

import config
from common.base import LoginAndSignTemplate
from common.base_config import BaseUserConfig
from utils.crypt_utils import rsa_encrypt, aes_encrypt, aes_decrypt
from utils.generator_utils import uuid_generator, rates_generator
from utils.ocr_utils import slide_match
from web.cloudpan.tyyun.scheme import *


# 天翼云盘
class TY(LoginAndSignTemplate):
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

    def other_task_run(self):
        """
        其他的任务执行入口，默认执行签到任务（无需再次添加，只需要实现了_sign方法即可）
        :return:
        """
        ret = []

        if self.check_run_task_permission("lucky"):
            # 抽奖任务
            if self._lucky():
                self.lock_task("lucky")
                ret.append(True)
        else:
            self.print("今日抽奖任务已完成!")

        return all(ret)

    def last_task_run(self):
        # 打印用户信息任务（方便统计）
        self._print_userinfo()

    def _set_files_dir(self):
        return os.path.dirname(__file__)

    def _check_expire(self) -> bool:
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
            self.print("检查cookie是否过期异常，原因：", e)
            return True

    def _print_userinfo(self):
        userinfo = self._get_userinfo()
        if userinfo is not None and userinfo["res_message"] == "成功":
            userinfo = UserInfoData.model_validate(userinfo)
            self.print(
                f"用户空间容量：\n可用{round(userinfo.available / 1073741824, 2)} GB\n总共{round(userinfo.capacity / 1073741824, 2)} GB")
        else:
            self.print("获取用户信息失败")

    def _get_userinfo(self):
        """
        获取用户信息
        :return:
        """
        url = "https://cloud.189.cn/api/open/user/getUserInfoForPortal.action"

        response = self.session.get(url, headers=self._base_headers)

        try:
            return response.json()
        except:
            self.print(response.text)
            return None

    def _lucky(self):
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
                    self.print(f"抽奖序号: {lucky_index} 请勿重复抽奖, 今日已经抽奖")
                else:
                    self.print(f"抽奖序号: {lucky_index} 抽奖成功, 获得抽奖奖励: {res_json.get('description')}")
                ret.append(True)
            except Exception as e:
                self.print(f"抽奖序号: {lucky_index} 抽奖异常, 原因：{e}")
                ret.append(False)
        return all(ret)

    def _sign(self):
        """
        签到
        :return:
        """
        sign_url = "https://m.cloud.189.cn/mkt/userSign.action"

        response = self.session.get(sign_url)
        try:
            res_json = response.json()
            bonus = res_json.get('netdiskBonus')
            if res_json.get("isSign"):
                self.print(f"请勿重复签到, 今日已经获得签到奖励: {bonus}M空间")
            else:
                self.print(f"签到成功, 获得签到奖励: {bonus}")
            return True
        except Exception as e:
            self.print(f"签到异常, 原因：{e}")
            return False

    def _login(self):
        """
        登录帐号
        :return:
        """
        try:
            self.__prepare_for_login()
        except ImportError as e:
            self.print(e)
            return False
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
        try:
            res_json = response.json()
            msg = res_json.get("msg")
            if msg == "密码不正确":
                self.print("密码不正确")
                return False
            elif msg == "登录成功":
                # 获取重定向链接（主要是为了更新代表用户的cookie）
                toUrl = res_json.get("toUrl")
                # 发送重定向请求
                self.session.get(toUrl)
                """
                {
                    "result":0,
                    "msg":"登录成功",
                    "toUrl":"https://cloud.189.cn/api/portal/callbackUnify.action?redirectURL=https://cloud.189.cn/web/redirect.html&appId=cloud&paras=448D3CA2233C4B8067BAE1A20938BE3F15C87BD77C2B45277D619A0B5FB5D9E8B0A72D7A546E85C4F77BD94E784990B3746266E26A9EEA821D4DE0F1F1A90F0C4A6D47A5648B1ADE9B21C1CBE2F07B003418693D26BE1389985E56BD393999B7968F053D61482FAE33CC38E54D03F42B1BC38E748AC6384E64001CB5D96D3BB29AF7E61C03CD0468D915E51A99D64D96CDE4307EFD57C3878A4B1F858BED3A25AF730CE55A49DEFB20ED6E9156E7393C526B7A025587EF9180214D942E3B1B52CC75122B0BDF05BEB8ADB0FCE5DE79896220A0C1606D1BFAEFEA778905F0818A6598E7A3F6EECD64A2F842F6CE9D9CCBB7AE5A79A2BB7169B8D90B0ABF5526D5356B9CA4E5836A7704A5BF0400004E2E5901A5BD0AEACBA8D1FDB94396A1BEB3464B62950BD3A0EEEC7DA358683D4424B969EA04B3FE3F4A63E0B46B89DB60E983842A41434DB4CE0B88D4AB6AB926EDA14B798CC19F4161F79A369DA46C7D3EA78E6A2395CE55B5F0E080CC7B3504EC8290A620C8491C8E347E7BF5B1C4CE84A96897665FA9BC65B94C386D83FC5BFD160E5C8FF2DFB689AA7BF7400E46B64749E24B8FED7642CFA8A2ED9B48E50264A934D1014484710A62EFEA1776368BBCFFAC212B2CC91028AB83250F00C968CC4DDC8FE3&sign=F530B3B8F9B81A8EFCF9620192961FDEF9D55896"
                }
                """
                return True
            else:
                self.print(res_json)
                return False
        except:
            self.print(response.text)
            return False

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
            self.print("检测到需要进行滑块拼图验证")
            attempts = 3
            self.print(f"正在尝试（{attempts}次）后台自动破解...")
            for attempt in range(attempts):
                self.print(f"正在尝试第{attempt + 1}次破解...")
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
                    self.print("滑块验证码已通过!")
                    self.print("正在解密返回结果...")
                    pass_captcha_data = aes_decrypt(pass_en_data, b64_uuid)
                    self.__pass_captcha_data = PassCaptchaData.model_validate_json(pass_captcha_data)
                    self.print("解密成功!")
                    break
                else:
                    self.print("滑块验证码破解失败!")

    def __fetch_redirect_url(self, request_url: str):
        """
        提取重定向链接
        :param request_url: 请求链接
        :return: 重定向链接
        """
        # 发送请求，并停止重定向
        response = self.session.get(request_url, headers=self._base_headers, allow_redirects=False)
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
        response = self.session.post(captcha_url, headers=self._base_headers, data=data)
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
        self.__save_captcha_image(target_image_base64, "target.png")
        # 保存背景图片
        self.__save_captcha_image(background_image_base64, "background.png")

    def __read_target_captcha_image(self):
        """
        读取目标图片
        :return:
        """
        with open(os.path.join(self._set_files_dir(), "target.png"), 'rb') as file:
            return file.read()

    def __read_background_captcha_image(self):
        """
        读取背景图片
        :return:
        """
        with open(os.path.join(self._set_files_dir(), "background.png"), 'rb') as file:
            return file.read()

    def __save_captcha_image(self, image_base64, file_name):
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
        with open(os.path.join(self._set_files_dir(), file_name), 'wb') as file:
            file.write(img_binary)

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

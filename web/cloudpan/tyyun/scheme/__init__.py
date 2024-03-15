# -*- coding: utf-8 -*-
# __init__.py.py created by MoMingLog on 13/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-13
【功能描述】
"""

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """
    appConf.do 相关响应数据
    """
    accountType: str = Field(..., description="账号类型")
    appKey: str = Field(..., description="appKey")
    clientType: int = Field(..., description="客户端类型")
    returnUrl: str = Field(..., description="回调地址")
    mailSuffix: str = Field(..., description="邮箱后缀")
    isOauth2: bool = Field(..., description="是否开启Oauth2")
    reqId: str = Field(..., description="请求ID")
    paramId: str = Field(..., description="参数ID")


class EncryptConfig(BaseModel):
    """
    encryptConf.do 相关响应数据
    """
    upSmsOn: str = Field(..., description="是否开启短信验证，0 或 1")
    pre: str = Field(..., description="加密数据的前缀")
    preDomain: str = Field(..., description="暂不知，只知道是个域名")
    pubKey: str = Field(..., description="公钥")


class CaptchaData(BaseModel):
    """
    拼图 相关响应数据
    """
    captchaType: int = Field(..., description="验证码类型，1：拼图")
    bg: str = Field(..., description="背景图")
    front: str = Field(..., description="前景图")
    token: str = Field(..., description="token")


class PassCaptchaData(BaseModel):
    """
    拼图通过验证 相关响应数据
    """
    captchaType: int = Field(default=1, description="验证码类型，1：拼图")
    token: str = Field(default="", description="token")
    validate_result: str = Field(default="", description="验证结果")


class UserInfoData(BaseModel):
    """
    用户信息 相关响应数据
    """
    res_code: int = Field(..., description="响应码")
    res_message: str = Field(..., description="响应信息")
    available: int = Field(..., description="可用空间")
    capacity: int = Field(..., description="总空间")

# -*- coding: utf-8 -*-
# base.py created by MoMingLog on 22/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-22
【功能描述】
"""
import os
from abc import abstractmethod, ABCMeta

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

import config

try:
    import ujson as json
except:
    import json


class SingletonMeta(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseFSStrategy(metaclass=SingletonMeta):
    """基本文件储存策略"""

    def __init__(self, *args, **kwargs):
        self._file_path = None
        self._filename = None

    @abstractmethod
    def init_config(self, *args, **kwargs):
        pass

    @abstractmethod
    def load(self) -> any:
        pass

    @abstractmethod
    def save(self, content: any):
        pass

    @property
    def project_path(self):
        return config.GlobalConfig.PROJECT_PATH

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @staticmethod
    def encrypt(content: str):
        salt = os.urandom(16)
        yield salt
        key = PBKDF2(config.GlobalConfig.AES_KEY, salt, 32)
        iv = os.urandom(16)
        yield iv
        cipher = AES.new(key, AES.MODE_CFB, iv)
        yield cipher.encrypt(content.encode('utf-8'))

    @staticmethod
    def decrypt(content):
        salt = content[:16]
        iv = content[16:32]
        ciphertext = content[32:]
        key = PBKDF2(config.GlobalConfig.AES_KEY, salt, 32)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        try:
            return cipher.decrypt(ciphertext).decode('utf-8')
        except:
            raise ValueError('解密错误，请检查密钥是否正确')

# -*- coding: utf-8 -*-
# local.py created by MoMingLog on 22/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-22
【功能描述】
"""
import os.path
import re

try:
    import ujson as json
except:
    import json
import config
from common.storage.base import BaseFSStrategy


class LocalFSStrategy(BaseFSStrategy):
    """本地文件储存策略"""

    def __init__(self):
        self.__cache = dict()
        self._hash_value = None

    def init_config(self, hash_value, task_name):
        """
        在load_config_data方法中调用此初始化方法

        主要用来初始化路径参数
        :param hash_value:
        :param task_name:
        :return:
        """
        self._hash_value = hash_value
        file_name = f"{hash_value}_{task_name}.json"
        root_dir_name = re.sub(r'[\\/:*?"<>|]', "_", task_name)
        root_dir_path = os.path.join(config.GlobalConfig.PROJECT_PATH, "files", root_dir_name)
        if not os.path.exists(root_dir_path):
            os.makedirs(root_dir_path)
        self.file_path = os.path.join(root_dir_path, file_name)

    def load(self) -> dict:
        ret_data = {}
        if os.path.exists(self.file_path):
            try:
                if not config.GlobalConfig.IS_ENCRYPT_SAVE:
                    with open(self.file_path, "r", encoding="utf-8") as f:
                        ret_data = json.load(f)
                else:
                    with open(self.file_path, "rb") as f:
                        ret_data = json.loads(self.decrypt(f.read()))
            except:
                pass
        return ret_data

    def save(self, user_data: dict):
        if not config.GlobalConfig.IS_ENCRYPT_SAVE:
            with open(self.file_path, "w") as fp:
                json.dump(user_data, fp)
        else:
            with open(self.file_path, "wb") as fp:
                fp.writelines(self.encrypt(json.dumps(user_data)))

    @property
    def file_path(self):
        return self.__cache.get("file_path")

    @file_path.setter
    def file_path(self, value):
        self.__cache["file_path"] = value

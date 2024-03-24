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
import global_config
from common.storage.base import BaseFSStrategy


class LocalFSStrategy(BaseFSStrategy):
    """本地文件储存策略"""

    def init_config(self, hash_value, task_name):
        """
        在load_config_data方法中调用此初始化方法

        主要用来初始化路径参数
        :param hash_value:
        :param task_name:
        :return:
        """
        self.filename = f"{hash_value}_{task_name}.json"
        root_dir_name = re.sub(r'[\\/:*?"<>|]', "_", task_name)
        root_dir_path = os.path.join(global_config.PROJECT_PATH, "files", root_dir_name)
        os.makedirs(root_dir_path, exist_ok=True)
        self.file_path = os.path.join(root_dir_path, self.filename)

    def load(self) -> dict:
        ret_data = {}
        if os.path.exists(self.file_path):
            try:
                if not global_config.IS_ENCRYPT_SAVE:
                    with open(self.file_path, "r", encoding="utf-8") as f:
                        ret_data = json.load(f)
                else:
                    with open(self.file_path, "rb") as f:
                        ret_data = json.loads(self.decrypt(f.read()))
            except FileNotFoundError:
                pass  # 文件不存在，返回空字典
            except json.JSONDecodeError:
                pass  # JSON 解析错误，返回空字典
            except Exception as e:
                raise Exception(f"加载本地文件失败，文件路径：{self.file_path}, 错误信息：{e}")
        return ret_data

    def save(self, user_data: dict):
        try:
            if not global_config.IS_ENCRYPT_SAVE:
                with open(self.file_path, "w") as fp:
                    json.dump(user_data, fp)
            else:
                with open(self.file_path, "wb") as fp:
                    fp.writelines(self.encrypt(json.dumps(user_data)))
        except Exception as e:
            raise Exception(f"保存本地文件失败，文件路径：{self.file_path}, 错误信息：{e}")

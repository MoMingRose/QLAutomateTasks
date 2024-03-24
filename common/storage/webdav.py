# -*- coding: utf-8 -*-
# webdav.py created by MoMingLog on 20/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-20
【功能描述】
"""
from webdav4.fsspec import WebdavFileSystem

import global_config
from common.storage.base import BaseFSStrategy

try:
    import ujson as json
except:
    import json

from common.base_config import WebDavConfig


class WebdavFSStrategy(BaseFSStrategy):

    def __init__(self, webdav_config: WebDavConfig = WebDavConfig(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.webdav_config = webdav_config
        if self.webdav_config.base_remote_dir.endswith("/"):
            self.webdav_config.base_remote_dir = self.webdav_config.base_remote_dir[:-1]

        self.fs: WebdavFileSystem = WebdavFileSystem(
            base_url=self.webdav_config.base_url,
            auth=(self.webdav_config.username, self.webdav_config.password)
        )

    def init_config(self, hash_value, task_name, *args, **kwargs):
        """
        初始化配置
        :param hash_value: 哈希值（用户名+任务名）
        :param task_name: 任务名
        :param args: 扩展参数
        :param kwargs: 扩展参数
        """
        # 文件名
        self.filename = f"{hash_value}_{task_name}.json"
        # 创建远程目录
        self.fs.makedirs(self.base_remote_dir, exist_ok=True)
        # 文件路径
        self.file_path = f"{self.base_remote_dir}/{task_name}/{self.filename}"

    def load(self) -> any:
        try:
            if global_config.IS_ENCRYPT_SAVE:
                # 如果是加密存储，则进行解密读取
                return json.loads(self.decrypt(self.fs.read_bytes(self.file_path)))
            else:
                # 直接读取内容
                return json.loads(self.fs.read_text(self.file_path))
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"加载文件失败，文件路径：{self.file_path}, 错误信息：{e}")

    def save(self, content: any):
        # 判断是否是字典或者列表
        if isinstance(content, dict | list):
            # 将字典或者列表转换为json字符串格式
            content = json.dumps(content)
        try:
            # 判断是否需要加密存储
            if global_config.IS_ENCRYPT_SAVE:
                # 加密储存
                with self.fs.open(self.file_path, 'wb') as f:
                    f.writelines(self.encrypt(content))
            else:
                # 不加密存储
                self.fs.write_text(self.file_path, content)
        except Exception as e:
            print(f"保存文件失败，文件路径：{self.file_path}, 错误信息：{e}")

    @property
    def base_remote_dir(self):
        return f"{self.webdav_config.base_remote_dir}/QLAutomateTasks"


if __name__ == '__main__':
    webdav_client = WebdavFSStrategy(
        webdav_config=WebDavConfig(
            base_url="http://192.168.1.11:5244/dav",
            username="test",
            password="test",
            base_remote_dir="/MoMingLog/123云盘"
        )
    )
    # # # Write to remote file
    # webdav_client.write("t/test.txt", [{"a": 1, "b": 2}])
    #
    # # # Read from remote file
    # print("Remote file contents:", webdav_client.read("t/test.txt"))

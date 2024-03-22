# -*- coding: utf-8 -*-
# webdav.py created by MoMingLog on 20/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-20
【功能描述】
"""
from webdav4.fsspec import WebdavFileSystem

import config
from common.storage.base import BaseFSStrategy

try:
    import ujson as json
except:
    import json

from common.base_config import WebDavConfig


class WebdavFSStrategy(BaseFSStrategy):
    _cache = {}

    def __init__(self, webdav_config: WebDavConfig = None):
        self.webdav_config = webdav_config

    def init_config(self, hash_value, task_name, *args, **kwargs):
        """
        初始化配置
        :param hash_value: 哈希值（用户名+任务名）
        :param task_name: 任务名
        :param args: 扩展参数
        :param kwargs: 扩展参数
        """
        # 文件名
        self.file_name = f"{hash_value}_{task_name}.json"
        # 判断是否已经缓存webdav配置
        if self.webdav_config is None:
            # 如果没有，则进行实例化并缓存
            self.webdav_config = WebDavConfig()
            if self.webdav_config.base_remote_dir.endswith("/"):
                self.webdav_config.base_remote_dir = self.webdav_config.base_remote_dir[:-1]
        # 判断webdav实例是否存在
        if self.fs is None:
            # 如果不存在，则创建
            self.fs = WebdavFileSystem(
                base_url=self.webdav_config.base_url,
                auth=(self.webdav_config.username, self.webdav_config.password)
            )
        # 初始化远程目录
        self.base_remote_dir = f"{self.webdav_config.base_remote_dir}/QLAutomateTasks"
        # 判断远程目录是否存在
        if not self.fs.exists(self.base_remote_dir):
            # 如果不存在则创建
            self.fs.mkdirs(self.base_remote_dir)
        # 文件路径
        self.file_path = f"{self.base_remote_dir}/{task_name}/{self._cache['file_name']}"

    def load(self) -> any:
        try:
            if config.GlobalConfig.IS_ENCRYPT_SAVE:
                # 如果是加密存储，则进行解密读取
                return json.loads(self.decrypt(self.fs.read_bytes(self.file_path)))
            else:
                # 直接读取内容
                return json.loads(self.fs.read_text(self.file_path))
        except FileNotFoundError:
            print("文件或者目录不存在")

    def save(self, content: any):
        # 判断是否是字典或者列表
        if isinstance(content, dict | list):
            # 将字典或者列表转换为json字符串格式
            content = json.dumps(content)
        try:
            # 判断是否需要加密存储
            if config.GlobalConfig.IS_ENCRYPT_SAVE:
                # 加密储存
                with self.fs.open(self.file_path, 'wb') as f:
                    f.writelines(self.encrypt(content))
            else:
                # 不加密存储
                self.fs.write_text(self.file_path, content)
        except FileNotFoundError:
            print("文件或者目录不存在")

    def ls(self, remote_dir: str = None):
        """
        列出远程目录下的信息
        :param remote_dir:
        :return:
        """
        try:
            if remote_dir is not None:
                remote_dir = f"{self.base_remote_dir}/{remote_dir}"
            else:
                remote_dir = self.base_remote_dir
            return self.fs.ls(remote_dir)
        except FileNotFoundError:
            print("文件或者目录不存在")
            return None

    # def write(self, remote_file_path: str, content: str | dict | list):
    #     """
    #     写入内容到远程文件
    #     :param remote_file_path: 远程文件路径（基于base_remote_dir）
    #     :param content: 写入的内容
    #     """
    #     # 判断是否是字典或者列表
    #     if isinstance(content, dict | list):
    #         # 将字典或者列表转换为json字符串格式
    #         content = json.dumps(content)
    #     try:
    #         # 判断是否需要加密存储
    #         if config.GlobalConfig.IS_ENCRYPT_SAVE:
    #             # 加密储存
    #             with self.fs.open(f"{self.base_remote_dir}/{remote_file_path}", 'wb') as f:
    #                 f.writelines(self.encrypt(content))
    #         else:
    #             # 不加密存储
    #             self.fs.write_text(f"{self.base_remote_dir}/{remote_file_path}", content)
    #     except FileNotFoundError:
    #         print("文件或者目录不存在")

    # def read(self, remote_file_path: str) -> str:
    #     """
    #     读取远程文件内容
    #     :param remote_file_path: 远程文件路径（基于base_remote_dir）
    #     :return:
    #     """
    #     try:
    #         if config.GlobalConfig.IS_ENCRYPT_SAVE:
    #             # 如果是加密存储，则进行解密读取
    #             return self.decrypt(self.fs.read_bytes(f"{self.base_remote_dir}/{remote_file_path}"))
    #         else:
    #             # 直接读取内容
    #             return self.fs.read_text(f"{self.base_remote_dir}/{remote_file_path}")
    #     except FileNotFoundError:
    #         print("文件或者目录不存在")

    def exists(self, remote_file_path: str) -> bool:
        """
        判断远程文件是否存在
        :param remote_file_path: 远程文件路径（基于base_remote_dir）
        :return:
        """
        return self.fs.exists(f"{self.base_remote_dir}/{remote_file_path}")

    @property
    def file_name(self):
        return self._cache.get("file_name")

    @file_name.setter
    def file_name(self, value):
        self._cache["file_name"] = value

    @property
    def file_path(self):
        return self._cache.get("file_path")

    @file_path.setter
    def file_path(self, value):
        self._cache["file_path"] = value

    @property
    def webdav_config(self):
        return self._cache.get("webdav_config")

    @webdav_config.setter
    def webdav_config(self, value):
        self._cache["webdav_config"] = value

    @property
    def base_remote_dir(self):
        return self._cache.get("base_remote_dir")

    @base_remote_dir.setter
    def base_remote_dir(self, value):
        self._cache["base_remote_dir"] = value

    @property
    def fs(self):
        return self._cache.get("fs")

    @fs.setter
    def fs(self, value):
        self._cache["fs"] = value

    # def __init__(self, webdav_config: WebDavConfig):
    #     if webdav_config.base_remote_dir.endswith("/"):
    #         webdav_config.base_remote_dir = webdav_config.base_remote_dir[:-1]
    #     self.base_remote_dir = f"{webdav_config.base_remote_dir}/QLAutomateTasks"
    #     self.fs = WebdavFileSystem(
    #         base_url=webdav_config.base_url,
    #         auth=(webdav_config.username, webdav_config.password)
    #     )
    #
    #     self.__init_remote_dir()

    # def __init_remote_dir(self):
    #     """
    #     初始化远程目录
    #     :return:
    #     """
    #     if not self.fs.exists(self.base_remote_dir):
    #         self.fs.mkdirs(self.base_remote_dir)


if __name__ == '__main__':
    webdav_client = WebdavFSStrategy(
        webdav_config=WebDavConfig(
            base_url="http://192.168.1.11:5244/dav",
            username="test",
            password="test",
            base_remote_dir="/MoMingLog/123云盘"
        )
    )
    print(webdav_client.ls("/"))
    # # # Write to remote file
    # webdav_client.write("t/test.txt", [{"a": 1, "b": 2}])
    #
    # # # Read from remote file
    # print("Remote file contents:", webdav_client.read("t/test.txt"))

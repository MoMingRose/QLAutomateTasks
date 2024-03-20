# -*- coding: utf-8 -*-
# webdav.py created by MoMingLog on 20/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-20
【功能描述】
"""
import os

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

import config

try:
    import ujson as json
except:
    import json

from webdav4.fsspec import WebdavFileSystem

from common.base_config import WebDavConfig


class WebDAVClient:
    def __init__(self, webdav_config: WebDavConfig):
        if webdav_config.base_remote_dir.endswith("/"):
            webdav_config.base_remote_dir = webdav_config.base_remote_dir[:-1]
        self.base_remote_dir = f"{webdav_config.base_remote_dir}/QLAutomateTasks"
        self.fs = WebdavFileSystem(
            base_url=webdav_config.base_url,
            auth=(webdav_config.username, webdav_config.password)
        )

        self.__init_remote_dir()

    def __init_remote_dir(self):
        """
        初始化远程目录
        :return:
        """
        if not self.fs.exists(self.base_remote_dir):
            self.fs.mkdirs(self.base_remote_dir)

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

    def write(self, remote_file_path: str, content: str | dict | list):
        """
        写入内容到远程文件
        :param remote_file_path: 远程文件路径（基于base_remote_dir）
        :param content: 写入的内容
        """
        # 判断是否是字典或者列表
        if isinstance(content, dict | list):
            # 将字典或者列表转换为json字符串格式
            content = json.dumps(content)
        try:
            # 判断是否需要加密存储
            if config.GlobalConfig.IS_ENCRYPT_SAVE:
                # 加密储存
                with self.fs.open(f"{self.base_remote_dir}/{remote_file_path}", 'wb') as f:
                    f.writelines(self.encrypt(content))
            else:
                # 不加密存储
                self.fs.write_text(f"{self.base_remote_dir}/{remote_file_path}", content)
        except FileNotFoundError:
            print("文件或者目录不存在")

    def read(self, remote_file_path: str) -> str:
        """
        读取远程文件内容
        :param remote_file_path: 远程文件路径（基于base_remote_dir）
        :return:
        """
        try:
            if config.GlobalConfig.IS_ENCRYPT_SAVE:
                # 如果是加密存储，则进行解密读取
                return self.decrypt(self.fs.read_bytes(f"{self.base_remote_dir}/{remote_file_path}"))
            else:
                # 直接读取内容
                return self.fs.read_text(f"{self.base_remote_dir}/{remote_file_path}")
        except FileNotFoundError:
            print("文件或者目录不存在")

    def exists(self, remote_file_path: str) -> bool:
        """
        判断远程文件是否存在
        :param remote_file_path: 远程文件路径（基于base_remote_dir）
        :return:
        """
        return self.fs.exists(f"{self.base_remote_dir}/{remote_file_path}")

    @staticmethod
    def encrypt(content) -> str:
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


if __name__ == '__main__':
    webdav_client = WebDAVClient(
        webdav_config=WebDavConfig(
            base_url="http://192.168.1.11:5244/dav",
            username="test",
            password="test",
            base_remote_dir="/MoMingLog/123云盘"
        )
    )
    # # Write to remote file
    webdav_client.write("t/test.txt", [{"a": 1, "b": 2}])

    # # Read from remote file
    print("Remote file contents:", webdav_client.read("t/test.txt"))

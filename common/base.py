# -*- coding: utf-8 -*-
# base.py created by MoMingLog on 5/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-05
【功能描述】模板
"""
import os
from abc import ABC, abstractmethod

import requests
import ujson as json

import config
from common.base_config import BaseTokenConfig, BaseConfig
from config import BaseUserConfig
from utils import base_utils
from utils.base_utils import fetch_account_list
from utils.crypt_utils import md5


class BaseTemplate(ABC):
    def __init__(self, userConfig: BaseConfig, default_env_key: str):
        """
        初始化
        :param userConfig: 用户配置实例
        :param default_env_key: 环境变量默认的 key （对应的value存储着账号密码数据）
        """

        self._tag = userConfig.tag
        self._env_key = userConfig.env_key if userConfig.env_key is not None else default_env_key

        self.session = requests.session()
        self._base_headers = self._generate_bash_headers()
        self.session.headers.update(self._base_headers)

        self.local_user_config = {}
        self.root_dir = os.path.join(
            self._set_files_dir(), "files") if not config.GlobalConfig.IS_DEBUG else os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "files")

    def _generate_bash_headers(self):
        """
        生成基础请求头
        :return:
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
            "Accept": "application/json;charset=UTF-8"
        }

    @abstractmethod
    def _sign(self):
        pass

    @abstractmethod
    def _set_files_dir(self):
        pass

    def _base_task_run(self, local_user_config_path: str):
        """
        基础任务运行
        :return:
        """
        # 判断是否拥有执行任务权限
        if self.check_run_task_permission("sign"):
            # 拥有签到权限，进行签到
            if self._sign():
                # 签到成功，锁定签到
                self.lock_task("sign", local_user_config_path)
        else:
            self.print("今日签到任务已完成!")
        if self.check_run_task_permission("other_task"):
            # 调用子类任务运行
            if self.other_task_run():
                # 子类任务运行成功
                self.lock_task("other_task", local_user_config_path)
        else:
            self.print("今日其他任务已完成!")

        self.last_task_run()

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    @abstractmethod
    def other_task_run(self):
        pass

    @abstractmethod
    def last_task_run(self):
        """
        最后执行的任务，这个方法不会检测执行权限，每次运行程序，必定执行的任务
        :return:
        """
        pass

    def load_local_user_config(self, path: str):
        """
        读取本地用户运行配置文件
        :param path: 文件路径
        :return:
        """
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fp:
                self.local_user_config = json.load(fp)

    def check_run_task_permission(self, task_name: str):
        """
        检查是否需要签到
        :param task_name: 任务名称
        :return:
        """
        # 判断是否存在 指定任务 数据
        if runtime := self.local_user_config.get(task_name):
            # 如果执行任务时间不是今天，返回True，否则返回False
            return not runtime == base_utils.get_today()

        # 不存在，返回True
        return True

    def lock_task(self, task_name: str, local_user_config_path: str):
        """
        锁定任务
        :param task_name 任务名称
        :param local_user_config_path: 本地用户配置文件路径
        :return:
        """
        self.local_user_config[task_name] = base_utils.get_today()
        self.flash_config(local_user_config_path)

    def __write_cookie(self, local_user_config_path: str):
        """
        存储cookie
        :param local_user_config_path: 本地用户配置文件路径
        :return:
        """
        self.local_user_config["cookie"] = self.session.cookies.get_dict()
        self.flash_config(local_user_config_path)

    def __load_cookie(self):
        """
        加载cookie
        :return:
        """
        cookie = self.local_user_config.get("cookie")
        if cookie:
            self.session.cookies.update(cookie)
            return True
        return False

    def flash_config(self, local_user_config_path: str):
        """
        刷新配置
        :param local_user_config_path: 本地用户配置文件路径
        :return:
        """
        with open(local_user_config_path, "w") as fp:
            json.dump(self.local_user_config, fp)


# TODO: 待完善
class TokenTemplate(BaseTemplate, ABC):
    """仅适用于token操作的模板"""

    def __init__(self, userConfig: BaseTokenConfig, default_env_key: str):
        super().__init__(userConfig, default_env_key)
        nickname = userConfig.nickname
        token = userConfig.token
        token_list = userConfig.token_list if userConfig.token_list is not None else list()

        if nickname is None or token is None:
            if userConfig.test_env is not None:
                # 使用测试环境变量值
                token_list = fetch_account_list(test_env=userConfig.test_env)
            else:
                if self._env_key is None:
                    raise AttributeError("未配置环境变量的key值，在不明确传入token的情况下，请务必配置！")
                # 未传入token，从环境变量中提取token
                token_list = fetch_account_list(env_key=self._env_key)
        else:
            token_list.append([nickname, token])

        self._token_list = token_list

        for nickname, token in self._token_list:
            self._msg_list = []
            self._nickname = nickname
            self._token = token
            self._hash_name = md5(nickname + self._tag)
            self.local_user_config_path = os.path.join(self.root_dir, f"{self._hash_name}_{self._tag}.json")
            self.load_local_user_config(self.local_user_config_path)

            # self.__prepare()
            self._base_task_run(self.local_user_config_path)

    def print(self, *args, **kwargs):
        print(self._nickname, ": ", *args, **kwargs)
        for arg in args:
            self._msg_list.append(arg)

    def result(self):
        return "\n".join(self._msg_list)


# TODO: 待修改
class LoginAndSignTemplate(ABC):
    """支持模拟登陆的模板"""

    def __init__(self, userConfig: BaseUserConfig, default_env_key: str):
        """

        :param userConfig: 用户配置实例
        :param default_env_key: 环境变量默认的 key （对应的value存储着账号密码数据）
        :param tag: 运行任务的标签
        """

        # 懒得改动太多直接在这里定义
        username = userConfig.username
        password = userConfig.password
        # 优先配置，其次默认
        env_key = userConfig.env_key if userConfig.env_key is not None else default_env_key
        # 判断是否传入账号列表（用来处理多账号）
        account_list = userConfig.account_list if userConfig.account_list is not None else list()
        tag = userConfig.tag

        self.session = requests.Session()
        self._base_headers = self._generate_bash_headers()
        self.session.headers.update(self._base_headers)

        # 判断是否传入账号密码
        if username is None or password is None:
            if userConfig.test_env is not None:
                # 使用测试环境变量值
                account_list = fetch_account_list(test_env=userConfig.test_env)
            else:
                if env_key is None:
                    raise AttributeError("未配置环境变量的key值，在不明确传入账号密码的情况下，请务必配置！")
                # 未传入账号密码，从环境变量中提取账号密码
                account_list = fetch_account_list(env_key=env_key)
        else:
            # 传入账号密码，添加到账号列表中
            account_list.append([username, password])

        self._account_list = account_list

        self.root_dir = self.__get_root_dir()

        for username, password in self._account_list:
            self.local_user_config = {}
            # 初始化账号密码
            self._username = username
            self._password = password
            # 初始化消息推送列表
            self._msg_list = list()
            # 计算哈希值
            self._hash_name = md5(username + tag)
            # 初始化本地配置文件路径
            self.local_user_config_path = os.path.join(self.root_dir, f"{self._hash_name}_{tag}.json")

            # 加载配置
            self.load_local_user_config(self.local_user_config_path)

            try:
                # 执行任务的前期准备
                self.__prepare()
                # 调用基础任务运行
                self._base_task_run()
            except Exception as e:
                self.print(e)

    def _generate_bash_headers(self):
        """
        生成基础请求头
        :return:
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
            "Accept": "application/json;charset=UTF-8"
        }

    def __get_root_dir(self):
        root_dir = os.path.join(self._set_files_dir(),
                                "files") if not config.GlobalConfig.IS_DEBUG else os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "files")

        # 确保目录存在
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

        return root_dir

    def load_local_user_config(self, path: str):
        """
        读取本地用户运行配置文件
        :return:
        """
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fp:
                self.local_user_config = json.load(fp)
        else:
            self.local_user_config = {}

    def _base_task_run(self):
        """
        基础任务运行
        :return:
        """
        # 判断是否拥有执行任务权限
        if self.check_run_task_permission("sign"):
            # 拥有签到权限，进行签到
            if self._sign():
                # 签到成功，锁定签到
                self.lock_task("sign")
        else:
            self.print("今日签到任务已完成!")
        if self.check_run_task_permission("other_task"):
            # 调用子类任务运行
            if self.other_task_run():
                # 子类任务运行成功
                self.lock_task("other_task")
        else:
            self.print("今日其他任务已完成!")

        self.last_task_run()

    def other_task_run(self):
        pass

    def last_task_run(self):
        """
        最后执行的任务，这个方法不会检测执行权限，每次运行程序，必定执行的任务
        :return:
        """
        pass

    @abstractmethod
    def _set_files_dir(self):
        pass

    @abstractmethod
    def _check_expire(self) -> bool:
        """
        检查cookie是否过期
        :return: cookie过期返回True，cookie未过期返回False
        """
        pass

    @abstractmethod
    def _sign(self):
        pass

    @abstractmethod
    def _login(self):
        pass

    def check_run_task_permission(self, task_name: str):
        """
        检查是否需要签到
        :return:
        """
        # 判断是否存在 指定任务 数据
        if runtime := self.local_user_config.get(task_name):
            # 如果执行任务时间不是今天，返回True，否则返回False
            return not runtime == self.__get_today()

        # 不存在，返回True
        return True

    def __get_today(self):
        """
        获取今天的日期
        :return:
        """
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def __prepare(self):
        """
        准备工作
        :return:
        """
        # 判断是否需要登录
        is_need_login = False
        # 加载cookie数据（实际直接将cookie更新到self.__session中）
        if self.load_cookie():
            # 判断cookie是否过期
            if self._check_expire():
                self.print(f"{self._username} cookie已过期，重新登录")
                # cookie过期，需要重新登录
                is_need_login = True
            else:
                self.print(f"{self._username} cookie未过期，使用本地cookie")
        else:
            # 加载失败表示cookie数据不存在，需要登录
            is_need_login = True

        # 判断是否需要登录
        if is_need_login:
            # 清空session
            self.session = requests.Session()
            self.session.headers.update(self._base_headers)
            # 判断是否登录成功
            if not self._login():
                raise AttributeError(f"{self._username}登录失败")
            else:
                self.print(f"{self._username}登录成功!")
                self.write_cookie()

    def lock_task(self, task_name: str):
        """
        锁定任务
        :param task_name 任务名称
        :return:
        """
        self.local_user_config[task_name] = self.__get_today()
        self.flash_config()

    def write_cookie(self):
        """
        存储cookie
        :return:
        """
        self.local_user_config["cookie"] = self.session.cookies.get_dict()
        self.flash_config()

    def load_cookie(self):
        """
        加载cookie
        :return:
        """
        cookie = self.local_user_config.get("cookie")
        if cookie:
            self.session.cookies.update(cookie)
            return True
        return False

    def flash_config(self):

        with open(self.local_user_config_path, "w") as fp:
            json.dump(self.local_user_config, fp)

    def print(self, *args, **kwargs):
        print(self._username, ": ", *args, **kwargs)
        for arg in args:
            self._msg_list.append(arg)

    def result(self):
        return "\n".join(self._msg_list)

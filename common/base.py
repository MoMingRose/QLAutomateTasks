# -*- coding: utf-8 -*-
# base.py created by MoMingLog on 5/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-05
【功能描述】模板
"""
from abc import ABC, abstractmethod
from typing import List, Tuple

import requests

from common.storage.local import LocalFSStrategy
from common.storage.webdav import WebdavFSStrategy

try:
    import ujson as json
except:
    import json

import global_config
from common.base_config import BaseTaskConfig
from utils import base_utils
from utils.base_utils import fetch_account_list
from utils.crypt_utils import md5


class BaseTemplate(ABC):
    def __init__(self, taskConfig: BaseTaskConfig, *args, **kwargs):
        """
        初始化
        :param taskConfig: 用户配置实例，里面有四种账号传递方式（账号密码/账号列表传入、env_key、test_env），仅有一种生效
        :param default_env_key: 环境变量默认的 key （对应的value存储着账号密码数据）
        :param args: 扩展参数
        :param kwargs: 扩展参数
        """
        # 初始化存放推送消息的列表
        self.push_msg_list = []

        # 初始化任务标签
        self.task_name = taskConfig.task_name

        # 判断此任务是否可用
        if not taskConfig.task_enable:
            print(f"{self.task_name}任务不可用，跳过此任务")
            self.push_msg_list.append(f"{self.task_name}任务不可用, 跳过此任务")
            return

        # 初始化账号列表
        self.account_list = self.build_account_list(taskConfig, kwargs, *args)

        if self.account_list is None:
            raise Exception("账号列表为空，请确认子类中实现了build_account_list方法")
        t = 0
        x = {
            0: "0️⃣",
            1: "1️⃣",
            2: "2️⃣",
            3: "3️⃣",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
            10: "🔟"
        }

        # 遍历账号列表中的所有账号
        for username, password in self.account_list:
            s = x[t] * 4
            # 初始化请求相关数据
            self.session = requests.Session()
            self.base_headers = self.build_base_headers()
            self.session.headers.update(self.base_headers)

            # 初始化用户账号配置数据
            self.user_data = self.load_config_data(username, password, *args, **kwargs)
            # 初始化推送用户名, 如果环境变量IS_SEND_REAL_NAME为True，则显示实际用户名，否则显示其他
            self.print_username = f"【{username}】" if global_config.IS_PRINT_REAL_NAME else f"【账号{t}】"
            self.push_username = f"【{username}】" if global_config.IS_SEND_REAL_NAME else f"【账号{t}】"
            self.push_msg_list.append(f"{s}{self.push_username}{s}")

            # 初始化账号密码
            self._username = username
            self._password = password
            # 开始运行任务
            try:
                # 执行任务的前期准备任务
                self.__prepare_task_run(username, password, *args, **kwargs)
                # 执行基础任务
                self._base_task_run(username, password, *args, **kwargs)
            except AttributeError as e:
                self.push_msg("⁉️" + str(e))
            except Exception as e:
                self.push_msg("❌ " + str(e))

            finally:
                if t < 10:
                    t += 1
                else:
                    t = 0
                self.push_msg(f"{s}{self.push_username}{s}", is_print=False)

    @abstractmethod
    def build_account_list(self, taskConfig: BaseTaskConfig, *args, **kwargs) -> List[list]:
        """
        构建要运行任务的账号列表
        :param taskConfig: 用户配置
        :param args: 扩展参数
        :param kwargs: 扩展参数
        :return: 格式如：[[账号1，密码2], [账号2, 密码2], [昵称1, token1], [昵称2, cookie2]]的列表
        """
        pass

    @abstractmethod
    def load_config_data(self, username: str, password: str, *args, **kwargs) -> dict:
        """
        加载当前用户的配置数据
        :param username: 用户名
        :param password: 密码
        :param args: 扩展参数
        :param kwargs: 扩展参数
        :return: 返回字典数据
        """
        pass

    @abstractmethod
    def storage_data(self):
        """
        将当前用户的配置数据进行存储
        :return:
        """
        pass

    def lock_task(self, task_name: str, ):
        """
        锁定任务的运行（决定此任务是否可以再次运行）

        实际上就是给当前任务名字添加一个运行时间，然后再直接将当前用户配置数据进行储存

        可以选择重写，毕竟默认每次锁定任务都是将所有配置数据进行储存更新
        :param task_name 任务名称
        :return:
        """
        self.user_data[task_name] = base_utils.get_today()
        self.storage_data()

    @abstractmethod
    def build_base_headers(self) -> dict:
        """
        基础请求头
        :return: 字典类型数据
        """
        pass

    @abstractmethod
    def fetch_primary_data(self, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        """
        获取主要数据（从网络请求的响应中获取）

        如果是登录获取响应头中的set-cookie的话，可以直接返回bool类型
        因为请求完成后session中会自动记录cookie
        :return: 返回bool类型或者元祖类型数据，如果是元祖类型则：第一个元素是key值，第二个元素是value值，第三个元素是bool值（用来判断是否需要写入headers中）
        """
        pass

    @abstractmethod
    def get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        """
        获取主要数据（从已加载的配置中获取）

        例如，代表用户身份的数据不同，有的请求中使用cookie、有的使用Authorization、有的则表现在请求链接中

        故需要重写此方法，直接返回代表用户身份的

        :param current_user_config_data: 当前用户配置数据。从此参数中获取主要数据
        :return: bool类型或元祖类型数据，第一个元素是key值，第二个元素是value值，第三个元素是bool值（用来判断是否需要写入headers中）
        """
        pass

    @abstractmethod
    def check_expire_task_run(self) -> bool:
        """
        检查主要数据是否过期
        :return: 过期返回True，未过期返回False
        """
        pass

    @abstractmethod
    def sign_task_run(self, *args, **kwargs) -> bool:
        """
        签到任务运行的方法

        :param args: 扩展参数
        :param kwargs: 扩展参数
        :return: 运行成功返回True，否则返回False
        """
        pass

    @abstractmethod
    def other_task_run(self, *args, **kwargs) -> bool:
        """
        其他任务运行的方法

        需要增加运行任务时，将调用语句写进此方法体中即可
        :param args: 扩展参数
        :param kwargs: 扩展参数
        :return: 运行成功返回True，否则返回False
        """
        pass

    @abstractmethod
    def last_task_run(self, *args, **kwargs):
        """
        最后执行的任务，这个方法不会检测执行权限，每次运行程序，必定执行的任务
        :param args: 扩展参数
        :param kwargs: 扩展参数
        :return: 无
        """
        pass

    def __pack_sign_task(self, *args, **kwargs) -> bool | None:
        """
        打包签到任务
        :param args: 扩展参数
        :param kwargs: 扩展参数
        :return: 运行成功返回True，否则返回False 无需签到返回None
        """
        # 判断默认执行的签到任务是否具有执行权限
        if self.check_run_task_permission("sign"):
            res = self.sign_task_run(*args, **kwargs)
            if res:
                self.lock_task("sign")
            return res
        else:
            self.push_msg("✅ 今日签到任务已完成!")
            return True

    def __pack_other_task(self, *args, **kwargs) -> bool | None:
        """
        打包其他任务
        :param args: 扩展参数
        :param kwargs: 扩展参数
        :return: 运行成功返回True，否则返回False 无需执行返回None
        """
        # 判断默认执行的其他任务是否具有执行权限
        if self.check_run_task_permission("other_task"):
            res = self.other_task_run(*args, **kwargs)
            # 如果返回None，则表示此方法体内部没有实现
            if res is None:
                # 为了避免触发不必要的重试，直接返回True
                return True
            if res:
                self.lock_task("other_task")
            return res
        else:
            self.push_msg("✅ 今日其他任务已完成!")
            return True

    def __pack_last_task(self, *args, **kwargs):
        """
        打包最后任务
        :param args: 扩展参数
        :param kwargs: 扩展参数
        :return:
        """
        self.last_task_run(*args, **kwargs)

    def __pack_get_primary_data(self, current_user_config_data: dict) -> bool | Tuple[str, any, bool]:
        try:
            return self.get_primary_data(current_user_config_data)
        except Exception as e:
            self.push_msg(e, is_push=False)
            return False

    def __pack_fetch_primary_data(self, primary_key, *args, **kwargs):
        """
        打包获取主要数据
        :param primary_key: 主要数据的key
        :return: 运行成功返回True，否则返回False
        """
        result = self.fetch_primary_data(*args, **kwargs)

        if result:
            self.push_msg(f"{primary_key} 获取成功", is_push=False)
            self.save_cookie()
            if isinstance(result, bool):
                return False
            return result
        else:
            # 关键数据都没获取成功，那么当前账号的任务可以直接停止了
            raise Exception(f"{primary_key} 获取失败，停止执行任务")

    def __prepare_task_run(self, *args, **kwargs):
        """
        前期准备任务
        :return:
        """
        # 执行此方法前，所有与用户配置的数据均以加载完毕

        primary_key = "关键数据"

        def temp(data: tuple):
            nonlocal primary_key

            # 获取主要数据
            primary_key, primary_value, is_write_headers = data
            # 判断是否需要写入到请求头中
            if primary_key == "cookie":
                # 例如：从文件读取的cookie需要这样加载
                self.session.cookies.update(primary_value)
            elif is_write_headers:
                self.session.headers[primary_key] = primary_value
            self.user_data[primary_key] = primary_value
            self.storage_data()

        # 从已加载的配置中获取主要数据
        local_data = self.__pack_get_primary_data(self.user_data)

        if local_data and isinstance(local_data, tuple):
            temp(local_data)
            # 定义Flag，判断是否需要获取
            is_need_fetch = False

            if self.check_expire_task_run():
                self.push_msg(f"{primary_key} 已过期，需要重新获取!")
                is_need_fetch = True
            else:
                self.push_msg(f"{primary_key} 未过期，无需重新获取", is_push=False)

            if is_need_fetch:
                self.session = requests.Session()
                self.session.headers.update(self.base_headers)

                res_data = self.__pack_fetch_primary_data(primary_key, *args, **kwargs)
                if res_data:
                    temp(res_data)
        else:
            self.push_msg(f"{primary_key} 不存在，正在发起网络请求获取...", is_push=False)
            res_data = self.__pack_fetch_primary_data(primary_key, *args, **kwargs)
            if res_data:
                temp(res_data)

    def _base_task_run(self, *args, **kwargs):
        """
        基础任务运行
        :param args: 扩展参数
        :param kwargs: 扩展参数
        :return:
        """
        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            if self.__pack_sign_task(*args, **kwargs) and self.__pack_other_task(*args, **kwargs):
                break
            else:
                # 如果其中一个任务返回 False，则重新尝试
                continue
        self.__pack_last_task(*args, **kwargs)

    def check_run_task_permission(self, task_name: str) -> bool:
        """
        检查此任务是否具有执行权限（今天是否没有执行）
        :param task_name: 任务名称
        :return: True 可以执行 False 无需再次执行
        """
        # 判断是否存在 指定任务 数据
        if runtime := self.user_data.get(task_name):
            # 如果执行任务时间不是今天，返回True，否则返回False
            return not runtime == base_utils.get_today()

        # 如果此任务不存在（没有这个字段），返回True
        return True

    def push_msg(self, *args, is_print=True, is_push=True, **kwargs, ):
        """
        推送消息
        :param args:
        :param is_print: 是否打印
        :param is_push: 是否推送
        :param kwargs:
        :return:
        """
        if is_print:
            # 先在本地打印
            print(self.print_username, *args, **kwargs)
        # 再将推送消息存放到列表中
        for arg in args:
            if is_push and isinstance(arg, str):
                self.push_msg_list.append(arg)

    def save_cookie(self):
        """
        存储cookie
        :return:
        """
        cookie = self.session.cookies.get_dict()
        if cookie:
            self.user_data["cookie"] = cookie
            self.storage_data()

    def get_push_msg(self) -> str:
        """
        获取推送消息
        :return:
        """
        if len(self.push_msg_list) == 1:
            return self.push_msg_list[0]
        return "\n".join(self.push_msg_list)

    @property
    def result(self):
        return self.get_push_msg()

    def __str__(self):
        return self.get_push_msg()


class BaseQLTemplate(BaseTemplate, ABC):

    def __init__(self, taskConfig: BaseTaskConfig, default_env_key: str, *args, **kwargs):

        # 初始化环境变量key: 如果传入的环境变量key不存在，则使用默认的key（需要在子类__init__中传入）
        self.env_key = taskConfig.env_key if taskConfig.env_key is not None else default_env_key

        super().__init__(taskConfig, default_env_key, *args, **kwargs)

    def build_account_list(self, taskConfig: BaseTaskConfig, *args, **kwargs) -> List[list]:
        """
        青龙面板所属的构建账号列表的方式（从环境变量中读取）
        :param taskConfig:
        :param args:
        :param kwargs:
        :return:
        """
        account_list = []
        # 判断是否传入账号密码（其实就是判断是否是单账号，不推荐直接传入）
        if taskConfig.username is None or taskConfig.password is None:
            if self.env_key is not None:
                # 使用正式环境变量中的账号密码
                account_list = fetch_account_list(
                    env_key=self.env_key,
                    up_split=taskConfig.up_split,
                    ups_split=taskConfig.ups_split
                )
            else:
                # 否则直接抛出异常
                raise AttributeError(
                    "请检查以下参数是否正确传入（选一个）: \n 1. 账号密码/昵称&token\n 2. 环境变量key\n3. 测试变量test_env")
        else:
            # 如果传入了账号密码，合并到账号列表中（懒得判断是否传入账号列表了，直接把它们合并）
            account_list.append([taskConfig.username, taskConfig.password])

        return account_list


class BaseFSTemplate(BaseQLTemplate, ABC):
    """仅适用于文件存储的模板"""

    def __init__(self, taskConfig: BaseTaskConfig, default_env_key: str):
        # md5加密（后面文件名要用到）
        self._hash_value = ""
        # 文件名（包含文件后缀）
        self._file_name = ""
        # 加载策略
        self._load_strategy = taskConfig.load_strategy
        # 存储策略
        self._save_strategy = taskConfig.save_strategy

        self.load_storage = None
        self.save_storage = {}
        super().__init__(taskConfig, default_env_key)

    def load_config_data(self, username: str, password: str, *args, **kwargs) -> dict:
        self._hash_value = md5(username + self.task_name)

        if 1 in self._save_strategy:
            self.save_storage["local"] = {
                "storage": LocalFSStrategy(),
                "init": False
            }
        if 2 in self._save_strategy:
            self.save_storage["webdav"] = {
                "storage": WebdavFSStrategy(),
                "init": False
            }

        for strategy in self.save_storage.values():
            strategy["storage"].init_config(self._hash_value, self.task_name)
            strategy["init"] = True

        is_init = False
        if self._load_strategy == 1:
            # 通过本地文件方式加载用户配置数据
            local = self.save_storage.get("local")
            self.load_storage = LocalFSStrategy() if local is None else local["storage"]
            is_init = local.get("init") if local is not None else False
        elif self._load_strategy == 2:
            # 通过webdav文件方式加载用户配置数据
            webdav = self.save_storage.get("webdav")
            self.load_storage = WebdavFSStrategy() if webdav is None else webdav["storage"]
            is_init = webdav.get("init") if webdav is not None else False

        # 判断是否初始化
        if not is_init:
            self.load_storage.init_config(self._hash_value, self.task_name)

        # 开始从目标文件加载数据
        return self.load_storage.load()

    def storage_data(self):
        for strategy in self.save_storage.values():
            try:
                strategy['storage'].save(self.user_data)
            except Exception as e:
                self.push_msg(f"数据存储失败! 信息如下：\n> 文件路径：{strategy['storage'].file_path}\n> 错误信息：{e}")


class BaseFSTemplateForToken(BaseFSTemplate, ABC):
    """仅适用于令牌获取的模板"""

    def __init__(self, taskConfig: BaseTaskConfig, default_env_key: str):
        super().__init__(taskConfig, default_env_key)

    @abstractmethod
    def fetch_primary_data(self, nickname: str, token: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        pass

    @abstractmethod
    def sign_task_run(self, nickname: str, token: str, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    def check_token_is_expire(self, token: str) -> bool:
        pass

    def check_expire_task_run(self) -> bool:
        token = self._password
        return self.check_token_is_expire(token)


class BaseFSTemplateForAccount(BaseFSTemplate, ABC):
    """仅适用于账号获取的模板"""

    def __init__(self, taskConfig: BaseTaskConfig, default_env_key: str):
        super().__init__(taskConfig, default_env_key)

    @abstractmethod
    def fetch_primary_data(self, username: str, password: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        pass


class BaseFSTemplateForCookie(BaseFSTemplate, ABC):
    """仅适用于cookie获取的模板"""

    def __init__(self, taskConfig: BaseTaskConfig, default_env_key: str):
        super().__init__(taskConfig, default_env_key)

    def fetch_primary_data(self, nickname: str, cookie: str, *args, **kwargs) -> bool | Tuple[str, any, bool]:
        cookie_dict = requests.cookies.cookiejar_from_dict(
            {c.split('=')[0]: c.split('=')[1] for c in cookie.split(';') if c.strip()})
        self.session.cookies.update(cookie_dict)
        return True
        # return "cookie", cookie_dict, True

    def check_expire_task_run(self) -> bool:
        if self.check_cookie_is_expire():
            raise Exception("cookie已过期，请重新获取")
        return False

    @abstractmethod
    def check_cookie_is_expire(self):
        pass

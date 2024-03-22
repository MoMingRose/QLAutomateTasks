# -*- coding: utf-8 -*-
# config.py created by MoMingLog on 11/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-11
【功能描述】
"""
import os

from common.base_config import BaseTaskConfig
from utils.os_utils import get_env_value


class GlobalConfig:
    # 控制台打印是否使用真实的账号/昵称，默认打印真实账号/昵称
    IS_PRINT_REAL_NAME: bool = get_env_value("IS_PRINT_REAL_NAME", True)
    # 消息推送是否使用真实的账号/昵称，默认推送“【账号0/1/2/3/4/5/6/7/8/9】”
    IS_SEND_REAL_NAME: bool = get_env_value("IS_SEND_REAL_NAME", False)
    # 是否调试运行任务，与下方调试任务列表关联
    IS_DEBUG_TASKS: bool = get_env_value("IS_DEBUG_TASKS", False)
    # 要调试的任务列表，与上方调试开关关联
    DEBUG_TASKS_LIST: list = get_env_value("DEBUG_TASKS_LIST", [])
    # 是否加密存储，默认开启
    IS_ENCRYPT_SAVE: bool = get_env_value("IS_ENCRYPT_SAVE", True)
    # AES加密密钥
    AES_KEY: str = get_env_value("STORAGE_AES_KEY", "L*FN2m&b>CQe+=G;tVrp.S")
    # webdav开关，默认关闭
    WEBDAV_ENABLE: bool = get_env_value("WEBDAV_ENABLE", False)

    # 项目目录
    PROJECT_PATH = os.path.dirname(__file__)

    # 默认的依赖对照表
    DEPENDENCY_TABLE = {
        "python-dotenv": "dotenv",
        "pycryptodome": "Crypto",
    }


class DefaultTaskConfig:
    MIUIVERConfig = BaseTaskConfig(
        # 任务名称
        task_name="MIUIVER",
        # 任务描述
        task_desc='''
        MIUI刷机包签到，获取积分
        
        默认的环境变量为  miuiver_userinfo
        
        如果想修改，可以传入 env_key 参数
        ''',
        # 环境变量中存放账号数据的key（会按照这个值来查找，可以自定义）
        env_key="miuiver_userinfo",
        # 用来控制当前任务是否可用（默认为 True）
        task_enable=True,
        # 账号密码之间的分隔符，默认为 &
        up_split="&",
        # 多个账号之间的分隔符，默认为 |
        ups_split="|",
        # 设置加载策略，当前支持的策略有 1. local 2. webdav
        # 此设置方式优先级最高（会覆盖.env中的配置）
        # load_strategy=1,
        # 设置存储策略
        # save_strategy=[1]
    )

    XKProxyConfig = BaseTaskConfig(
        task_name="星空代理",
        task_desc='''
        签到领星币，星币可以兑换代理IP（爬虫练习时可用）
        
        默认环境变量为 xkdl_userinfo
        '''
    )

    V2EXConfig = BaseTaskConfig(
        task_name="V2EX",
        task_desc='''
        主页签到获取金币
        
        默认的环境变量为  v2ex_userinfo
        ''',
        # 修改多账号分隔符为 ||，因为cookie中包含单个 |
        ups_split="||"
    )

    JMKJConfig = BaseTaskConfig(
        task_name="芥末空间",
        task_desc='''
        主页签到获取芥子，版块签到获取经验
        
        默认的环境变量为  jmkj_userinfo
        '''
    )

    MTConfig = BaseTaskConfig(
        task_name="MT论坛",
        task_desc='''
        每日签到获取金币
        
        默认的环境变量为  mt_userinfo
        '''
    )

    TYYPConfig = BaseTaskConfig(
        task_name="天翼云盘",
        task_desc='''
        每日签到、抽奖获取空间
        
        默认的环境变量为  tyyp_userinfo
        '''
    )

    HLXConfig = BaseTaskConfig(
        task_name="葫芦侠三楼",
        task_desc='''
        版块签到获取经验
        
        默认的环境变量为  hlx_userinfo
        '''
    )

    ALYPConfig = BaseTaskConfig(
        task_name="阿里云盘",
        task_desc='''
        每日签到获取随机福利
        
        默认的环境变量为  alyp_userinfo
        '''
    )

    V2FreeConfig = BaseTaskConfig(
        task_name="V2Free",
        task_desc='''
        每日签到获取流量
        
        默认的环境变量为  v2free_userinfo
        ''',
        # 此任务当前已不可用
        task_enable=False,
    )

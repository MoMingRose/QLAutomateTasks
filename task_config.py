# -*- coding: utf-8 -*-
# task_config.py created by MoMingLog on 24/3/2024.
"""
【作者】MoMingLog
【创建时间】2024-03-24
【功能描述】
"""
from common.base_config import BaseTaskConfig

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

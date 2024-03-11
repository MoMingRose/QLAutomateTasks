#### 附赠一个花了几天自写的自动添加、更新、追加JD_COOKIE的软件 [去下载](https://github.com/MoMingRose/QLAutomateTasks/releases)

### 青龙面板拉库命令：

```shell
ql repo https://github.com/MoMingRose/QLAutomateTasks.git "一键" "" "*" "" "py|txt"
```

### 所需环境依赖如下:

已添加自动安装依赖脚本，运行“`一键任务执行.py`”脚本前，请先执行`一键依赖安装.py`脚本，执行完成后建议禁用此定时任务
> [!TIP]
> 如果是Docker拉取的青龙容器，建议拉取debian版本的，因为alpine不能安装ddddocr库（亲测）
> > 1. [ddddocr库](https://github.com/sml2h3/ddddocr)，我主要用来进行天翼云盘的滑块验证码识别，如果不介意天翼云盘用不了，可以选择不安装ddddocr依赖
> > 2. 当然，正常情况下是不会跳出来验证码，自然就用不到ddddocr库

### 此项目支持的签到任务状态如下

🟢: 正常运行 🔴: 暂不可用

⚪: 暂未添加 ⭕: 已经移除


| 状态 | 任务名称                                  | 检查日期       | 备注                                                                                                                                                 |
|----|---------------------------------------|------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| 🟢 | 葫芦侠三楼                                 | 2024.03.11 |                                                                                                                                                    |
| 🟢 | 芥末空间                                  | 2024.03.11 |                                                                                                                                                    |
| 🟢 | [阿里云盘](https://www.alipan.com/)       | 2024.03.11 |                                                                                                                                                    |
| 🟢 | [天翼云盘](https://cloud.189.cn/)         | 2024.03.11 |                                                                                                                                                    |
| 🟢 | [MT论坛](https://bbs.binmt.cc/)         | 2024.03.11 |                                                                                                                                                    |
| 🟢 | [MIUI历史版本(刷机包)](https://miuiver.com/) | 2024.03.11 |                                                                                                                                                    |
| 🔴 | [V2Free](https://v2free.net/)         | 2024.03.11 | <font style="color:red">已更换验证方式，目前暂不可用</font><br/><s>需要进行google的人机验证<br>愿意的话可以前往[【yescaptcha邀请链接】](https://yescaptcha.com/i/jFtvBe)获取ClientKey</s> |

### 各个签到任务详情

> [!TIP]
> 统一单账号格式：`账号&密码`（分隔符`&`）\
> 统一多账号格式：`账号1&密码1|账号2&密码2`（分隔符`|`）
> > 不支持账号密码模拟登陆方式的任务格式同上\
> > 例如阿里云盘: `昵称&refresh_token`

| 任务名称                                                    | 多账号 | 默认环境变量             | 使用方式          | 功能                           |
|---------------------------------------------------------|-----|--------------------|---------------|------------------------------|
| 葫芦侠三楼                                                   | ✅   | `hlx_userinfo`     | 账号密码          | 全板块签到，领取经验                   |
| 芥末空间                                                    | ✅   | `jmkj_userinfo`    | 账号密码          | 1. 全板块签到，获取经验<br>2.主页签到，领取芥末 |
| [阿里云盘](https://www.alipan.com/)                         | ✅   | `alyp_userinfo`    | refresh_token | 每日签到，领取免费会员和空间               |
| [天翼云盘](https://cloud.189.cn/)                           | ✅   | `tyyp_userinfo`    | 账号密码          | 每日签到，领取空间                    |
| [MT论坛](https://bbs.binmt.cc/?fromuid=123380)            | ✅   | `mt_userinfo`      | 账号密码          | 每日签到，领取金币                    |
| [MIUI历史版本(刷机包)](https://miuiver.com/)                   | ✅   | `miuiver_userinfo` | 账号密码          | 每日签到，领取固定1积分                 |
| [V2Free](https://w1.v2free.top/auth/register?code=8EZr) | ✅   | `v2free_userinfo`  | 账号密码          | 每日签到，领流量                     |

### 阿里云盘 refresh_token 获取方式

[去查看](docs/aliyun.md)

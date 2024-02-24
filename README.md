### 青龙面板拉库命令：

```shell
ql repo https://github.com/MoMingRose/QLAutomateTasks.git "一键任务执行" "docs|gitignore|README" "common|software|utils|web|config.py|notify.py"
```

### 所需环境依赖如下:

> [!TIP]
> 如果是Docker拉取的青龙容器，建议拉取debian版本的，因为alpine不能安装ddddocr库（亲测）
> > 1. [ddddocr库](https://github.com/sml2h3/ddddocr)，我主要用来进行天翼云盘的滑块验证码识别，如果不介意天翼云盘用不了，可以选择不安装ddddocr依赖
> > 2. 当然，正常情况下是不会跳出来验证码，自然就用不到ddddocr库

```text
pydantic
requests
rsa
pycryptodome
ujson 
python-dotenv 
ddddocr
```

### 此项目支持的签到任务状态如下

🟢: 正常运行 🔴: 脚本暂不可用 ⚪：脚本未添加 ⭕：脚本已移除

| 状态 | 任务名称                                  | 检查日期       | 备注                          |
|----|---------------------------------------|------------|-----------------------------|
| 🟢 | 葫芦侠三楼                                 | 2024.02.24 |                             |
| 🟢 | 芥末空间                                  | 2024.02.24 |                             |
| 🟢 | [阿里云盘](https://www.alipan.com/)       | 2024.02.24 |                             |
| 🟢 | [天翼云盘](https://cloud.189.cn/)         | 2024.02.24 |                             |
| 🟢 | [MT论坛](https://bbs.binmt.cc/)         | 2024.02.24 |                             |
| 🟢 | [MIUI历史版本(刷机包)](https://miuiver.com/) | 2024.02.24 |                             |
| ⚪  | [V2Free](https://v2free.net/)         | 2024.02.24 | 需要进行google的人机验证（目前我不知道如何解决） |

### 各个签到任务详情

> [!TIP]
> 统一单账号格式：`账号&密码`（分隔符`&`）\
> 统一多账号格式：`账号1&密码1|账号2&密码2`（分隔符`|`）
> > 不支持账号密码模拟登陆方式的任务格式同上\
> > 例如阿里云盘: `昵称&refresh_token`

| 任务名称                                  | 多账号 | 默认环境变量             | 使用方式          | 功能                           |
|---------------------------------------|-----|--------------------|---------------|------------------------------|
| 葫芦侠三楼                                 | ✅   | `hlx_userinfo`     | 账号密码          | 全板块签到，领取经验                   |
| 芥末空间                                  | ✅   | `jmkj_userinfo`    | 账号密码          | 1. 全板块签到，获取经验<br>2.主页签到，领取芥末 |
| [阿里云盘](https://www.alipan.com/)       | ✅   | `alyp_userinfo`    | refresh_token | 每日签到，领取免费会员和空间               |
| [天翼云盘](https://cloud.189.cn/)         | ✅   | `tyyp_userinfo`    | 账号密码          | 每日签到，领取空间                    |
| [MT论坛](https://bbs.binmt.cc/)         | ✅   | `mt_userinfo`      | 账号密码          | 每日签到，领取金币                    |
| [MIUI历史版本(刷机包)](https://miuiver.com/) | ✅   | `miuiver_userinfo` | 账号密码          | 每日签到，领取固定1积分                 |

### 阿里云盘 refresh_token 获取方式

[去查看](docs/aliyun.md)

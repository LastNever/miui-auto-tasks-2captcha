# MIUI Auto Tasks (2captcha)

基于 [0-8-4/miui-auto-tasks](https://github.com/0-8-4/miui-auto-tasks) 的 fork，集成了 [2captcha](https://2captcha.com/) 付费验证码服务，解决原项目免费验证方案不稳定/无法使用的问题。

![Python](https://img.shields.io/badge/python-3.7+-blue)
![GitHub](https://img.shields.io/github/license/0-8-4/miui-auto-tasks)

## Fork 修改内容

| 修改文件 | 说明 |
| --- | --- |
| `requirements.txt` | 新增 `2captcha-python==1.5.1` 依赖 |
| `utils/captcha.py` | 新增 `get_validate_by_2captcha()` 函数，调用 2captcha Geetest API |
| `utils/config.py` | `Preference` 类新增 `two_captcha_api_key` 配置项 |
| `utils/data_model.py` | `GeetestResult` 新增 `taskId` 字段，用于上报验证结果 |
| `utils/utils.py` | 验证码逻辑分支：有 key 走 2captcha，无 key 走原有逻辑；验证结果自动上报 |
| `firstrun.sh` | 仓库路径适配 |

**验证逻辑**：配置了 `two_captcha_api_key` 时自动使用 2captcha 服务，未配置时回退到原有的免费验证方案。验证成功/失败会自动上报给 2captcha（正确反馈可降低费用）。

## 快速开始

### 1. 获取 2captcha API Key

前往 [2captcha.com](https://2captcha.com/) 注册账号并充值，获取 API Key。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

首次运行会自动生成 `data/config.json`（或 `data/config.yaml`），编辑配置文件：

```json
{
    "preference": {
        "two_captcha_api_key": "你的2captcha-API-Key"
    },
    "accounts": [
        {
            "uid": "你的小米账号ID",
            "password": "密码或MD5",
            "login_user_agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Safari/537.36",
            "CheckIn": true,
            "BrowseUserPage": true,
            "BrowsePost": true
        }
    ]
}
```

**配置说明**：

| 字段 | 说明 |
| --- | --- |
| `preference.two_captcha_api_key` | 2captcha API Key，留空则使用免费验证方案 |
| `accounts[].uid` | 小米账号 ID（非手机号） |
| `accounts[].password` | 密码明文或 32 位 MD5 哈希 |
| `accounts[].login_user_agent` | 登录用 User-Agent，**必须为手机端 UA**（**必填，需手动配置**） |
| `accounts[].cookies` | 登录后的 cookies（可选，有则跳过登录） |
| `accounts[].CheckIn` | 社区签到开关 |
| `accounts[].BrowseUserPage` | 浏览个人主页开关 |
| `accounts[].BrowsePost` | 浏览帖子开关 |
| `accounts[].BrowseVideoPost` | 浏览视频帖子开关 |
| `accounts[].ThumbUp` | 点赞帖子开关 |
| `accounts[].WxSign` | 微信小程序签到开关 |

多账号在 `accounts` 数组中添加多个对象即可。

### 4. 运行

```bash
python miuitask.py
```

## Docker 部署

```bash
# 构建镜像
docker build -t miui-auto-tasks .

# 运行容器（首次运行后编辑 data/config.json 配置参数）
docker run -d \
    --name miui-auto-tasks \
    -v $(pwd)/data:/srv/data \
    -v $(pwd)/logs:/srv/logs \
    miui-auto-tasks
```

容器内通过 crontab 定时执行，每天凌晨 4 点运行，随机延迟 0-30 分钟。首次运行后进入容器编辑配置：

```bash
docker exec -it miui-auto-tasks vi /srv/data/config.json
```

## 青龙面板部署

1. **订阅仓库**：青龙面板 -> 订阅管理 -> 添加订阅

   - 类型：GitHub
   - 链接：`https://github.com/LastNever/miui-auto-tasks-2captcha`
   - 分支：`master`

2. **运行环境配置**：订阅成功后，青龙会自动拉取 `firstrun.sh`，首次运行会自动安装依赖。运行一次后**禁用**该任务。

3. **配置参数**：前往 脚本管理 -> `LastNever_miui-auto-tasks-2captcha_master` -> `data` -> `config.json` 中编辑配置。

4. **添加定时任务**：

   - 命令：`task LastNever_miui-auto-tasks-2captcha_master/miuitask.py`
   - 定时规则：`0 4 * * *`（每天凌晨 4 点，建议添加随机延迟）

## 注意事项

- 使用前请临时关闭网络代理和广告拦截
- 首次运行必须手动配置 `login_user_agent`（**手机端** User-Agent，不可使用桌面浏览器 UA），登录成功后 cookie 会自动写入配置文件，后续运行无需重复登录
- 服务器/容器部署时，首次运行如密码登录失败会自动触发二维码扫码登录（终端显示二维码）
- 配置文件默认禁用了大部分功能，请按需启用
- 使用本脚本产生的后果需自行承担

## 原项目

- 项目来源：[0-8-4/miui-auto-tasks](https://github.com/0-8-4/miui-auto-tasks)
- 详细使用说明请查看原项目：[WiKi](https://github.com/0-8-4/miui-auto-tasks/wiki)

## License

[MIT License](LICENSE) - Copyright (c) 2021 東雲研究所

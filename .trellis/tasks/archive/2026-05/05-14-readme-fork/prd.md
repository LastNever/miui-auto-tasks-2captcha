# 更新 README

## 目标
重写 README.md，让用户快速了解这个 fork 的定位、修改内容，并能快速上手使用。

## 内容要求

### 1. 项目简介
- 说明这是 miui-auto-tasks 的 fork
- 核心改动：集成 2captcha 付费验证码服务，解决原项目免费验证方案不稳定的问题

### 2. Fork 修改说明
- 新增 `2captcha-python` 依赖
- 新增 `get_validate_by_2captcha()` 函数
- 配置新增 `two_captcha_api_key` 字段
- `GeetestResult` 新增 `taskId` 字段用于上报验证结果
- 验证码逻辑分支：有 key 走 2captcha，无 key 走原有逻辑
- `firstrun.sh` 路径适配

### 3. 使用方法
- 本地运行：安装依赖、配置 config、运行
- Docker 部署
- 青龙面板部署

### 4. 配置说明
- config.json / config.yml 结构
- two_captcha_api_key 的位置和获取方式

## 不变的部分
- MIT License 保持不变
- 鸣谢部分保留原项目贡献者信息

#!/usr/bin/env bash
# new Env("MIUI-Auto-Task 环境配置")
echo "在本任务运行完后请不要忘记禁用该任务！"
echo "在本任务运行完后请不要忘记禁用该任务！"
echo "在本任务运行完后请不要忘记禁用该任务！"
echo "————————————"
echo "开始安装依赖"
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r /ql/data/repo/LastNever_miui-auto-tasks-2captcha_master/requirements.txt
echo "依赖已安装完毕"
echo "————————————"
echo "开始首次执行"
task LastNever_miui-auto-tasks-2captcha_master/miuitask.py
echo "首次执行完毕"
echo "————————————"
echo "请不要忘记禁用该任务！"
echo "请不要忘记禁用该任务！"
echo "请不要忘记禁用该任务！"
echo "请到 脚本管理 - LastNever_miui-auto-tasks-2captcha_master - data - config.yml 中配置参数"
echo "————————————"

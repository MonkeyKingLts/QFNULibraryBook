"""登录测试：读取 config.yml，打印验证码与 IDS 登录过程日志。"""
import logging
import os
import yaml

from get_bearer_token import get_bearer_token

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
with open(config_path, encoding="utf-8") as f:
    config = yaml.safe_load(f)

username = config["USERNAME"]
print("学号:", username)
print("密码长度:", len(config["PASSWORD"]))

name, token = get_bearer_token(username, config["PASSWORD"])
if token:
    print("登录成功，姓名:", name)
else:
    print("登录失败，请查看上方日志（验证码识别 / IDS 跳转）")

# QFNULibraryBook

曲阜师范大学图书馆预约程序

## 项目简介

本项目是一个用于曲阜师范大学图书馆座位预约的自动化脚本，旨在为有学习需求的同学提供便捷的预约方式，帮助大家更高效地利用学习资源。

## 免责声明和使用声明

本脚本仅供学习使用，使用本脚本预约图书馆座位后，请合理、有效地利用座位时间进行学习，以免占用其他有需求同学的学习资源。

**注意事项：**

1. 使用本脚本预约座位后，请按时前往图书馆学习。不得恶意占用座位或空占资源。
2. 本项目不对因违规使用或不当操作而导致的任何后果承担责任。
3. 请自觉遵守图书馆的相关规定，合理使用学习资源，共同维护良好的学习环境。

本项目为公益性质，任何滥用行为与开发者无关。开发者保留在必要时对项目进行调整或关闭的权利。

## 功能特点

- **多种预约模式**：提供三种预约模式，满足不同需求
- **自动签到签退**：支持自动签到和签退功能
- **多渠道通知**：支持钉钉、Telegram、Bark、Anpush等通知方式
- **Docker部署**：提供Docker容器化部署方案，方便快捷

## 快速启动

### 前提条件

- Python 3.12.1（Python 3.10+）
- 运行环境：Windows 10、Ubuntu 20.04、MacOS 12.0+ 或 Docker环境

### 安装依赖

```bash
pip install -r py/requirements.txt
```

### 配置程序

打开配置文件 `py/config.yml`，根据注释修改配置项：

1. `USERNAME`：图书馆账号
2. `PASSWORD`：图书馆密码
3. `PUSH_METHOD`：通知方式（可选值：TG、ANPUSH、BARK、DD）
4. 对应通知方式的相关配置

### 钉钉机器人通知

预约成功、失败或签退时，脚本可通过钉钉群机器人推送消息。配置步骤如下：

#### 1. 创建机器人

1. 打开钉钉群聊 → **群设置** → **智能群助手** → **添加机器人**
2. 选择 **自定义** 机器人，设置名称（如「图书馆预约」）
3. 安全设置建议选择 **加签**，复制页面上的 **SEC 开头的密钥**（即 `DD_BOT_SECRET`）
4. 完成后会得到 Webhook 地址，格式类似：

```
https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxx
```

#### 2. 填写配置文件

编辑 `py/config.yml`，填入以下三项：

```yaml
PUSH_METHOD: "DD"

# Webhook 地址中 access_token= 后面的字符串
DD_BOT_TOKEN: "xxxxxxxx"

# 创建机器人时「加签」方式得到的 SEC 密钥
DD_BOT_SECRET: "SECxxxxxxxx"
```

**示例：**

若 Webhook 为 `https://oapi.dingtalk.com/robot/send?access_token=abc123`，则：

- `DD_BOT_TOKEN` 填 `abc123`
- `DD_BOT_SECRET` 填创建时复制的 `SEC...` 密钥

#### 3. 注意事项

- `PUSH_METHOD` 必须填字母 **`DD`**，不要填数字 `4`
- 本项目使用 **加签** 方式鉴权，`DD_BOT_TOKEN` 和 `DD_BOT_SECRET` **两项都要填写**
- 请勿将 Token、Secret 提交到公开仓库（`config.yml` 已在 `.gitignore` 中）
- 通知在预约脚本结束或出现异常时发送，内容包括预约结果、座位信息等

#### 4. 其他通知方式

| PUSH_METHOD | 说明 | 需填写的配置项 |
|-------------|------|----------------|
| TG | Telegram | `CHANNEL_ID`、`TELEGRAM_BOT_TOKEN` |
| BARK | Bark 推送 | `BARK_URL`、`BARK_EXTRA` |
| ANPUSH | Anpush | `ANPUSH_TOKEN`、`ANPUSH_CHANNEL` |
| DD | 钉钉 | `DD_BOT_TOKEN`、`DD_BOT_SECRET` |

### 程序介绍

- `py/get_seat_tomorrow_mode_1.py`：预约模式 1，预约明天的座位，仅适用于西校区图书馆的三个自习室，优选了有插座的位置。
- `py/get_seat_tomorrow_mode_2.py`：预约模式 2，预约明天的座位，指定模式，需要预先根据 json/seat_info 中各个自习室的真实位置('name')获取座位代号('id')。
- `py/get_seat_tomorrow_mode_3.py`：预约模式 3，预约明天的座位，默认模式，全随机预约，速度最快，成功的概率最大。
- `py/sign_out.py`：签退程序，签退图书馆。
- `py/check_in.py`：签到程序，签到图书馆。该功能属于**违规操作**，请务必**谨慎使用**。

### 运行方式

#### 直接运行

```bash
# 运行预约模式1
python py/get_seat_tomorrow_mode_1.py

# 运行预约模式2
python py/get_seat_tomorrow_mode_2.py

# 运行预约模式3
python py/get_seat_tomorrow_mode_3.py

# 运行签到
python py/check_in.py

# 运行签退
python py/sign_out.py
```

#### Docker运行

详细的Docker部署指南请参考 [DEPLOY.md](DEPLOY.md) 文件。

## 与原作者的区别

二次开发者对原作者的程序进行了以下修改：

- 分离了预约模式 1、2、3，并分别进行了部分重构。
- 删除了预约当日的设置，只保留预约明天的设置。
- 删除了重新预约功能（原模式 5）
- 增加了钉钉机器人通知功能，可在配置文件中配置。
- 增加了签到功能，感谢开发者 [@nakaii-002](https://github.com/nakaii-002) 的贡献。
- 增加了Docker部署支持，方便在不同环境中运行。

以上被删除的功能如有需要，可以自行前往`old_py`目录下查看。

## 其他版本

基于此项目优化后的版本：

在根目录的 v3.1 目录下，感谢 https://github.com/CunchuanHuang 提供的优化版本。增加了西区二楼的，把一些数据存储格式也改了一些，config 文件中设置选座的格式也稍有调整。

## 贡献者

- [@W1ndys](https://github.com/W1ndys)：二次开发者
- [@sakurasep](https://github.com/sakurasep)：原作者
- [@nakaii-002](https://github.com/nakaii-002)：签到功能贡献者，获取身份验证 Auth_Token 的实现，自动获取 token 的实现

## 开源许可协议

本项目是由 [W1ndys](https://github.com/W1ndys) 基于 [上杉九月](https://github.com/sakurasep) 的 开源项目 [qfnuLibraryBook](https://github.com/sakurasep/qfnuLibraryBook) 二次开发，使用 CC BY-NC 4.0 协议进行授权，拷贝、分享或基于此进行创作时请遵守协议内容：

```
Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

This is a human-readable summary of (and not a substitute for) the license. You are free to:

Share — copy and redistribute the material in any medium or format
Adapt — remix, transform, and build upon the material

The licensor cannot revoke these freedoms as long as you follow the license terms.
Under the following terms:

Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

NonCommercial — You may not use the material for commercial purposes.

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

Notices:

You do not have to comply with the license for elements of the material in the public domain or where your use is permitted by an applicable exception or limitation.
No warranties are given. The license may not give you all of the permissions necessary for your intended use. For example, other rights such as publicity, privacy, or moral rights may limit how you use the material.
```
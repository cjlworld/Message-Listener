# Message Listener

Message Listener 是一个能主动监听网站，并将新发布的信息 以 Link card 的形式转发到钉钉群的脚本。

Message Listener 每次解析网站上的链接，并与之前的链接数据比对，将新发布的链接转发到钉钉群。因此如果您有订阅网站内容的需求，可以尝试将 该项目 添加到 您的定时任务 中。

## 如何部署

首先 clone 该项目到本地

```
git clone https://github.com/cjlworld/Message-Listener.git
```

**配置 config.json**

在 脚本文件 的目录下 添加 config.json 文件

示例:

```json
{
    "DING_WEBHOOK": "...",
    "DING_SECRET": "...",
    "urls": [
        "https://sample.com",
        "..."
    ],
}
```

先创建一个 DingDing Webhook机器人, 将 webhook 和 secret 填入 `DING_WEBHOOK` 和 `DING_SECRET`。

[自定义机器人的创建和安装 | 机器人概述 - 钉钉开放平台 - Ding Talk](https://open.dingtalk.com/document/orgapp/custom-bot-creation-and-installation)

在 `"urls"` 列表里添加您想订阅的网站即可。

**部署计划任务**

可以利用系统的计划任务功能直接部署（如 Windows 的 任务计划程序 和 Linux 的 crontab），也可以部署在 支持 python 定时任务程序上（如 青龙面板）。

项目里提供了一个 `.bat` 脚本，用于启动 windows 的定时任务。
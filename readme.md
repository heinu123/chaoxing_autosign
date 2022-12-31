>**本项目基于https://github.com/mkdir700/chaoxing_auto_sign/tree/master/local 修改**

>**PS:因本人已放寒假不需要上网课，无法排除可能存在的bug。如果遇到bug可以提交issues**


## 相关配置

**mode.ini**是签到脚本的配置文件

**user.json**需要签到的账号即密码(支持添加多个用户)

## mode.ini配置

> 签到模式：
sign(立即签到) timing(定时循环签到)

```
[global]
mode=sign
```

> 定时循环签到间隔时长:
默认5分钟执行一次签到任务
```
[time]
MINUTES=5
SECONDS=0
```
> 推送模式
telegram 使用telegram机器人发送签到成功消息
server 使用server酱发送签到成功消息
all 两个一起
```
[push]
mode=server
```

> telegram机器人的token和你的chat_id
搜索 @MissRose_bot 机器人 启用后发送 /info 指令即可获得你的chat_id
搜索 @BotFather 机器人生成你的bot 将机器人API token填入token即可
具体教程谷歌百度一抓一大把
```
[telegram]
token=
chat_id=
```

> server酱KEY(签到成功后发送推送消息)
申请地址:https://sct.ftqq.com/sendkey
```
[server]
key=
```

> 图片签到上传的图片(从目录中随机抽取一张)
```
[image]
PATH=./image/
```

> 位置签到提交的经纬度
```
[location]
longitude=121.469329
latitude=31.228518
```

> 位置签到提交的ip
```
[clientip]
ip=0.0.0.0
```
## user.json配置
```
[
    {
        'username': '',# 学习通账号
        'password': '', # 学习通密码
        'schoolid': ''  # 学号登录才需要填写
    },
]
```

## 运行
```
pip install -r requirements.txt #安装依赖
python main.py
```
或者直接运行[releases](https://github.com/mkdir700/chaoxing_auto_sign/tree/latest/api)里的编译后的可执行文件

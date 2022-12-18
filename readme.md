>**本项目基于https://github.com/mkdir700/chaoxing_auto_sign/tree/master/local 修改**

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


## 运行
```
python main.py
```
或者直接运行[releases](https://github.com/mkdir700/chaoxing_auto_sign/tree/latest/api)里的编译后的可执行文件

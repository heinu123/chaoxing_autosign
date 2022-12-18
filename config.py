import json
from configparser import ConfigParser
initext = ConfigParser()
initext.read('mode.ini')
f = open('user.json', 'r', encoding="utf-8")
USER_INFOS = []
USER_INFOS = eval(f.read())


MINUTES = initext.get('time', 'MINUTES')
SECONDS = initext.get('time', 'SECONDS')

SERVER_CHAN_SEND_KEY = initext.get('server', 'key')

COOKIES_PATH = "./"
COOKIES_FILE_PATH = COOKIES_PATH + "cookies.json"

ACTIVEID_PATH = "./"
ACTIVEID_FILE_PATH = ACTIVEID_PATH + "activeid.json"

IMAGE_PATH = initext.get('image', 'PATH')

location = (initext.get('location', 'longitude'), initext.get('location', 'latitude'))
longitude, latitude = location

clientip = initext.get('clientip', 'ip')

STATUS_CODE_DICT = {
    1000: '登录成功',
    1001: '登录信息有误',
    1002: '拒绝访问',
    2000: '当前暂无签到任务',
    2001: '有任务且签到成功',
    4000: '未知错误'
}


from datetime import datetime
from typing import List, Dict

import aiohttp

from config import SERVER_CHAN_SEND_KEY


async def server_chan_send(dataset):
    """
    dataset:
    [
        {
            'username': 'xx',
            'result': [
                {
                    'name': '',
                    'date': '',
                    'status': ''
                },
                ...
            ]
        }
    ]
    server酱将消息推送
    """
    if not SERVER_CHAN_SEND_KEY:
        print("SERVER_CHAN_SEND_KEY为空，不发送签到通知")
        return
    
    msg = ("| 账号 | 课程名 | 签到时间 | 签到状态 |\n"
           "| :----: | :----: | :------: | :------: |\n")
    msg_template = "|  {}  |  {}  | {}  |    {}    |\n"
    
    for datas in dataset:
        username = datas['username']
        result = datas['result']
        if len(result) == 0:
            return
        
        for data in result:
            msg += msg_template.format(username, data['name'], data['date'], data['status'])
        
    params = {
        'title': '您的网课签到消息来啦！',
        'desp': msg
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method="GET",
            url="https://sctapi.ftqq.com/{}.send?title=messagetitle".format(SERVER_CHAN_SEND_KEY),
            params=params
        ) as resp:
            await resp.text()

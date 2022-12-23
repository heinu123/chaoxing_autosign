from datetime import datetime
from typing import List, Dict

import aiohttp

from config import CHAT_ID
from config import SERVER_CHAN_SEND_KEY
from config import TELEGRAM_BOT_TOKEN


async def server_chan_send(dataset):
    if not SERVER_CHAN_SEND_KEY:
        print("SERVER_CHAN_SEND_KEY为空，不发送签到通知")
        return
    
    msg = ("| 账号 | 课程名 | 签到时间 | 签到状态 |\n"
           "| :----: | :----: | :------: | :------: |\n")
    msg_template = "|  {}  |  {}  | {}  |    {}    |"
    
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

async def telegram_bot_send(dataset):
    if not TELEGRAM_BOT_TOKEN:
        print("telegram bot token为空，不发送签到通知")
        return
    if not CHAT_ID:
        print("telegram chat_id为空，不发送签到通知")
        return
        
    msg="账号:{}\n课程:{}\n签到时间:{}\n签到状态:{}"

    for datas in dataset:
        username = datas['username']
        result = datas['result']
        if len(result) == 0:
            return
    
        for data in result:
            telegramcode = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json={"chat_id": chat_id, "text": msg.format(username, data['name'], data['date'], data['status'])})
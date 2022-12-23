import asyncio
import time
from typing import Tuple

import click
from apscheduler.schedulers.blocking import BlockingScheduler

import config
from configparser import ConfigParser
from local_sign import AutoSign
from log import log_error_msg
from message import server_chan_send
from message import telegram_bot_send

initext = ConfigParser()
initext.read('mode.ini')
mode = initext.get('push', 'mode')
event_loop = asyncio.new_event_loop()


@log_error_msg
async def gen_run(username, password, enc=None):
    """运行"""
    auto_sign = AutoSign(username, password, enc=enc)
    result = await auto_sign.start_sign_task()
    # 关闭会话
    await auto_sign.close_session()
    return {
        'username': username,
        'result': result
    }


async def local_run():
    tasks = []
    print("=" * 50)
    print("[{}]".format(time.strftime('%Y-%m-%d %H:%M:%S')))
    for info in config.USER_INFOS:
        coro = gen_run(username=info['username'],
                       password=info['password'],
                       enc=info.get('enc', None))
        tasks.append(coro)
    results = await asyncio.gather(*tasks)
    if mode == "telegram":
        await telegram_bot_send(results)
    elif mode == "server":
        await server_chan_send(results)
    elif mode == "all":
        await telegram_bot_send(results)
        await server_chan_send(results)
    else:
        print("不存在的推送模式")
        return
    print("签到结果：")
    for res in results:
        print(res)



@click.group()
def cli():
    pass



def start():
    event_loop.run_until_complete(local_run())

@click.command()
def sign():
    """
    立即签到
    """
    start()

@click.command()
def timing():
    """
    定时签到
    """
    scheduler = BlockingScheduler()
    minutes = eval(config.MINUTES)
    seconds = eval(config.SECONDS)
    scheduler.add_job(start, 'interval', minutes=minutes, seconds=seconds)
    print('已开启定时执行,每间隔{}分{}秒执行一次签到任务'.format(minutes, seconds))
    scheduler.start()


if __name__ == '__main__':
    cli.add_command(sign)
    cli.add_command(timing)
    cli()
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler('logs.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_error_msg(func):
    def warp(*arg, **kwargs):
        try:
            return func(*arg, **kwargs)
        except Exception as e:
            logger.exception(e)
            return '程序执行出错,错误信息已在记录日志'
    
    return warp

import sign
from configparser import ConfigParser
initext = ConfigParser()
initext.read('mode.ini')
mode = initext.get('global', 'mode')


if mode == "sign":
  sign.start()
elif mode == "timing":
  sign.timing()
else:
  print("签到模式:\nsign    立即签到\n  timing  定时签到")
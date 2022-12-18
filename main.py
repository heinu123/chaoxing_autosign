import sign
from configparser import ConfigParser
initext = ConfigParser()
initext.read('mode.ini')
mode = initext.get('global', 'mode')

if mode == "sign":
  sign.start()
elif mode == "timing":
  sign.timing()
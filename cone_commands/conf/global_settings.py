import os
import sys


if sys.platform == 'win32':
    CONFIG_PATH = os.path.join(os.environ['USERPROFILE'], '.cone_commands')
else:
    CONFIG_PATH = os.path.join('/etc/', 'cone_commands')

if not os.path.exists(CONFIG_PATH):
    os.makedirs(CONFIG_PATH)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/98.0.4758.80 Safari/537.36'
}

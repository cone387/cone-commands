import os
import sys


if sys.platform == 'win32':
    CONFIG_PATH = os.path.join(os.environ['USERPROFILE'], '.cone_commands')
else:
    CONFIG_PATH = os.path.join('/etc/', 'cone_commands')

if not os.path.exists(CONFIG_PATH):
    os.makedirs(CONFIG_PATH)



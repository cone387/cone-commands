import sys
from cone_commands.core.management import execute_from_command_line


if __name__ == '__main__':
    cmd = r'myip'
    execute_from_command_line(sys.argv[:] + cmd.split(' '))

    # using json path
    cmd = r'myip'
    execute_from_command_line(sys.argv[:] + cmd.split(' '))

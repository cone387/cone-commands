import sys
from cone_commands.core.management import execute_from_command_line


if __name__ == '__main__':
    # using auto-detect items
    cmd = r'json --to-excel=. -f C:\Users\cone\Desktop\long_text_2023-04-26-17-20-30.txt'
    execute_from_command_line(sys.argv[:] + cmd.split(' '))

    # using json path
    cmd = r'json --to-excel=. -y -p=$.data.rows.* -f C:\Users\cone\Desktop\long_text_2023-04-26-17-20-30.txt'
    execute_from_command_line(sys.argv[:] + cmd.split(' '))

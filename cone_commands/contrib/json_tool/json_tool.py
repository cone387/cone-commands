import json
import pathlib
import sys
import jsonpath
from cone_commands.core.management.base import BaseCommand, Command
from typing import Union, Dict, List

Json = Union[Dict, List]


# 获取一个json中dict最多的一个list
def find_lists(data: Json, result=None) -> List[List[Dict]]:
    # 记住，这里的result是可变的，所以不要用result = result or []这种形式
    if result is None:
        result = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (list, dict)):
                find_lists(v, result)
    elif isinstance(data, list):
        # 这里判断是List[Dict]就够了，不需要判断每个Dict的key是否相同, 因为有些字段可以为空
        if all([isinstance(x, dict) for x in data]):
            result.append(data)
        else:
            for x in data:
                if isinstance(x, (list, dict)):
                    find_lists(x, result)
    return result


def find_max_list(data: Json) -> List[Dict]:
    lists = find_lists(data)
    return max(lists, key=lambda x: len(x))


def json_to_excel(data, excel: pathlib.Path, json_path=None):
    try:
        import pandas as pd
    except ImportError:
        print('pandas is required for json to excel, you can install it by pip install pandas')
        sys.exit(1)
    if json_path is None:
        items = find_max_list(data)
    else:
        items = jsonpath.jsonpath(data, json_path)
    if items is None:
        raise ValueError(f'no items can be extracted')
    df = pd.DataFrame(items)
    df.to_excel(excel, index=False)
    print(f'extracted {len(items)} items to {excel}')


@Command.register()
class JsonCommand(BaseCommand):

    name = 'json'

    def create_parser(self, prog_name, subcommand, **kwargs):
        parser = super(JsonCommand, self).create_parser(prog_name, subcommand, **kwargs)
        parser.add_argument('-f', '--file', type=str, help='json file', required=False)
        parser.add_argument('--to-excel', type=str, help='extract json to excel')
        parser.add_argument('-y', '--yes', action='store_true', help='yes to all')
        parser.add_argument('-p', '--path', type=str, help='json path')
        parser.add_argument('--auto-path', action='store_true', help='auto detect path for access json')
        return parser

    def handle(self, *args, file=None, path=None, to_excel=None, yes=False, **options):
        if not file:
            return self.print_help('json', '')
        file = pathlib.Path(file)
        if not file.exists():
            raise FileNotFoundError(f'{file} not found')
        with open(file, 'r', encoding='utf-8') as f:
            data: Json = json.load(f)
        if to_excel is not None:
            if to_excel == '.':
                excel = file.with_name(file.stem + '.xlsx')
            else:
                excel = pathlib.Path(to_excel)
            if excel.exists():
                if not yes:
                    yes = input(f'{to_excel} exists, overwrite? [y/n]') == 'y'
                if not yes:
                    return
            json_to_excel(data, excel, path)

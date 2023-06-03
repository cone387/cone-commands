import os
import json
from collections import OrderedDict
from cone_commands.core.management.base import BaseCommand, Command
from cone_commands.conf.global_settings import CONFIG_PATH
from cone.communication.ding_talk import DingRobot


@Command.register()
class DingTalkCommand(BaseCommand):
    name = 'dd'

    @property
    def config_path(self):
        return os.path.join(super(DingTalkCommand, self).config_path, 'dingtalk.json')

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='message', nargs='?')
        parser.add_argument('--config', action='store_true', help='add robot')
        parser.add_argument('--config-path', type=str, help='config path', default=self.config_path)

    @staticmethod
    def check_config(config):
        for k, v in config.items():
            if not v:
                raise ValueError(f'配置失败, {k} 不能为空')

    def config_robot(self, config_path):
        columns_mapping = OrderedDict(
            name='名称',
            token='token',
            secret='secret'
        )
        try:
            for k, v in columns_mapping.items():
                print(f'{v}:', end='')
                value = input()
                columns_mapping[k] = value
            self.check_config(columns_mapping)
        except KeyboardInterrupt:
            pass
        except ValueError as e:
            print(e)
        else:
            with open(config_path, 'w') as f:
                f.write(json.dumps(columns_mapping))
            print('配置成功')

    def send_msg(self, msg, config_path=None):
        config_path = config_path or self.config_path
        if not os.path.exists(config_path):
            return print('请先配置机器人, 使用 --config 参数')
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.check_config(config)
        robot = DingRobot(**config)
        robot.send_msg(msg)

    def handle(self, *args, message=None, **options):
        config_path = options['config_path']
        if options['config']:
            self.config_robot(config_path)
        elif not message:
            self.print_help('dd', '')
        else:
            self.send_msg(message, config_path)

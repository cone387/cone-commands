from cone_commands.core.management.base import BaseCommand, Command
from datetime import datetime
from cone.crypto import aes
from functools import partial
from typing import Dict, List
import os
import json
import getpass
import shutil


class Field:
    def __init__(self, name, t=str, description=None, default=None, required=False, get_input=None, input_prompt=None):
        self.name = name
        self.type = t
        self.default = default
        self.required = required
        self.description = description
        get_input = get_input or input
        if required:
            get_input = partial(get_required_filed_input, get_input, name=name, max_retry=3)
            if input_prompt is None:
                input_prompt = f'{name}(required): '
        self._get_input = get_input
        self.input_prompt = input_prompt or f'{name}: '

    def get_input(self):
        return self._get_input(self.input_prompt)

    def __str__(self):
        return self.name

    __repr__ = __str__


def get_required_filed_input(get_input, prompt, name=None, max_retry=3):
    for _ in range(max_retry):
        value = get_input(prompt)
        if value:
            return value
    raise ValueError(f'{name or "the input"} is required')


class Website:
    input_fields = ['name', 'url', 'user', 'password', 'tips']
    fields_mapping: Dict[str, Field] = {
        'name': Field('name', required=True, description='网站名称'),
        'url': Field('url', description='网站地址'),
        'user': Field('user', description='用户名'),
        'password': Field('password', required=True, description='密码', get_input=getpass.getpass),
        'tips': Field('tips', description='备注'),
    }

    def __init__(self, name=None, url=None, user=None, password=None, tips=None, create_time=None, **kwargs):
        self.name = name
        self.url = url
        self.user = user
        self.password = password
        self.tips = tips
        if create_time and isinstance(create_time, str):
            create_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
        self.create_time = create_time

    def to_json(self):
        return {
            'name': self.name,
            'url': self.url,
            'user': self.user,
            'password': self.password,
            'tips': self.tips,
            'create_time': (self.create_time or datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __str__(self):
        return "Website(name={name}, user={user}, tips={tips}, create_time={create_time}, url={url})".format(
            **self.to_json())

    __repr__ = __str__


@Command.register()
class PasswordCommand(BaseCommand):
    name = 'pwd'

    def list_websites(self):
        password_json = os.path.join(self.config_path, 'password.json')
        if not os.path.exists(password_json):
            return []
        websites = []
        with open(password_json, 'r') as f:
            content = json.load(f)
        for k, v in content.items():
            website = Website(**v)
            websites.append(website)
        return websites

    def search_websites(self, keyword: str, search_fields=None) -> List[Website]:
        search_fields = search_fields or ['name', 'url', 'user', 'tips']
        websites = self.list_websites()
        result = []
        for website in websites:
            for field in search_fields:
                if keyword in getattr(website, field):
                    result.append(website)
        return result

    def add_website(self, website: Website, encrypt_key: str):
        password_json = os.path.join(self.config_path, 'password.json')
        password_bak_json = os.path.join(self.config_path, 'password.bak.json')
        website.password = aes.encrypt(website.password, encrypt_key)
        if os.path.exists(password_json):
            shutil.copy(password_json, password_bak_json)
            with open(password_json, 'r') as f:
                content = json.load(f)
        else:
            content = {}
        if website.name in content:
            yes = input(f'{website.name} already exists, do you want to overwrite it?(y/n): ')
            if yes.lower() != 'y':
                return
        with open(password_json, 'w') as f:
            content[website.name] = website.to_json()
            json.dump(content, f)
        print("add success, you can use 'cone pwd %s' to get password" % website.name)

    def add_arguments(self, parser):
        parser.add_argument('option', type=str, help='add、list、query website password', nargs='?')
        parser.add_argument('-d', '--decrypt', action='store_true', help='decrypt password')

    def handle(self, *args, option=None, decrypt=False, **options):
        if option == 'add':
            website_password = Website()
            try:
                for key in website_password.input_fields:
                    field = website_password.fields_mapping[key]
                    setattr(website_password, key, field.get_input())
                encrypt_key = get_required_filed_input(getpass.getpass,
                                                       "encrypt key(Remember it, it wont be stored): ", 'encrypt_key',)
            except KeyboardInterrupt as e:
                print("exit")
                return
            self.add_website(website_password, encrypt_key)
        elif option == 'delete':
            pass
        elif option == 'list':
            websites = self.list_websites()
            print("%s websites found" % len(websites))
            for i, website in enumerate(websites):
                print(f'{i + 1}. {website}')
        elif option == 'update':
            pass
        elif option:
            websites = self.search_websites(keyword=option)
            print("%s websites found" % len(websites))
            for i, website in enumerate(websites):
                print(f'{i + 1}. {website}')
            if decrypt and websites:
                if len(websites) == 1:
                    website = websites[0]
                else:
                    index = int(input('which one do you want to decrypt, choose index: '))
                    website = websites[index - 1]
                encrypt_key = get_required_filed_input(getpass.getpass, "decrypt key: ")
                try:
                    password = aes.decrypt(website.password, encrypt_key)
                except UnicodeDecodeError:
                    self.stderr.write("decrypt failed, please check your decrypt key")
                else:
                    self.stdout.write("decrypt succeed: %s" % password)
        else:
            self.print_help('cone', 'pwd')

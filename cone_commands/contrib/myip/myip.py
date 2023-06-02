import requests
import socket
from cone_commands.conf.global_settings import HEADERS
from cone_commands.core.management.base import BaseCommand, Command


# 请求外网ip
def request_ip(url):
    return requests.get(url, headers=HEADERS).text


@Command.register()
class MyIPCommand(BaseCommand):
    query_url = 'http://members.3322.org/dyndns/getip'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--index', type=str, help='index', default=self.query_url)

    def handle(self, *args, **options):
        ip = request_ip(options['index'])
        print("外网ip: %s" % ip.strip())
        print("内网ip: %s" % socket.gethostbyname(socket.gethostname()))

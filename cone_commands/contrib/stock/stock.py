from cone_commands.core.management.base import BaseCommand, Command
from .base import StockItem, DataSource


@Command.register()
class KlineWatcher(BaseCommand):

    def create_parser(self, prog_name, subcommand, **kwargs):
        parser = super(KlineWatcher, self).create_parser(prog_name, subcommand, **kwargs)
        parser.add_argument('--data-source', type=str, help='data source', default='xueqiu')
        parser.add_argument('--code', type=str, help='stock code')
        parser.add_argument('--name', type=str, help='stock name')
        parser.add_argument('--date', type=str, help='date')
        return parser

    def handle(self, *args, **options):
        data_source = options['data_source']
        code = options['code']
        name = options['name']
        stock = StockItem(code=code, name=name)
        data_source = DataSource(data_source=data_source, is_registry=False)
        kline = data_source.request_kline(stock, options['date'])
        print(kline)

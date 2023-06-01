import time
import sys
from cone_commands.core.management.base import BaseCommand, Command
from .base import StockItem, DataSource
from datetime import datetime
from itertools import zip_longest
from typing import List, Dict


class Trigger:
    def __init__(self):
        pass


@Command.register()
class KlineWatcher(BaseCommand):

    def create_parser(self, prog_name, subcommand, **kwargs):
        parser = super(KlineWatcher, self).create_parser(prog_name, subcommand, **kwargs)
        parser.add_argument('--data-source', type=str, help='data source', default='xueqiu')
        parser.add_argument('--code', type=str, help='stock code')
        parser.add_argument('--name', type=str, help='stock name')
        parser.add_argument('--date', type=str, help='date')
        parser.add_argument('--forever', action='store_true', help='forever')
        parser.add_argument('--interval', type=int, help='interval', default=2)
        parser.add_argument('--columns', type=str, help='columns', default='*')
        return parser

    def on_price_changed(self, current, histories):
        """
            单次涨跌幅超过多少
            高于某个固定价格
            低于某个固定价格
            :param current:
            :param histories:
            :return:
        """

    @staticmethod
    def watch_forever(data_source: DataSource, stocks, interval=2, columns='*',):
        now = datetime.now()
        close_time = now.replace(hour=15, minute=0, second=0, microsecond=0)
        histories: Dict[str, List] = {}
        print("Start watching, press Ctrl+C to stop")
        try:
            while now < close_time:
                if (now.hour >= 9 and now.minute >= 30) and (now.hour <= 11 and now.minute <= 30) \
                        or (now.hour >= 13 and now.minute >= 0):
                    for stock in stocks:
                        kline = data_source.request_kline(stock, date=now)
                        stock_histories = histories.setdefault(stock.code, [])
                        if len(stock_histories) > 0:
                            last = stock_histories[-1]
                            if last.current != kline.current:
                                KlineWatcher.on_price_changed(kline, stock_histories)
                        stock_histories.append(kline)
                        print(kline.info(columns))
                else:
                    sys.stdout.write("\rMarket is sleeping, waiting for next open...")
                    sys.stdout.flush()
                time.sleep(interval)
                now = datetime.now()
        except KeyboardInterrupt:
            pass
        print("Market closed, Stop watching")

    def handle(self, *args, **options):
        code = options['code']
        name = options['name']
        stocks = [StockItem(code=x.strip(), name=y.strip()) for x, y in zip_longest(code.split(','), name.split(','))]
        data_source = DataSource(data_source=options['data_source'], is_registry=False)
        if options['forever']:
            self.watch_forever(data_source, stocks, interval=options['interval'], columns=options['columns'])
        else:
            for stock in stocks:
                kline = data_source.request_kline(stock, columns=options['columns'])
                print(kline.info(options['columns']))

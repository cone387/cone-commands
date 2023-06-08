import sys
import time
from cone_commands.core.management.base import BaseCommand, Command
from .trigger import Trigger, BaseTrigger
from .base import StockItem, DataSource, Receiver
from datetime import datetime
from itertools import zip_longest
from typing import List, Dict


@Command.register()
class KlineWatcher(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--data-source', type=str, help='data source', default='xueqiu')
        parser.add_argument('-c', '--code', type=str, help='stock code', default='')
        parser.add_argument('-n', '--name', type=str, help='stock name', default='')
        parser.add_argument('-d', '--date', type=str, help=r'date, format: Y-m-d, default: today')
        parser.add_argument('-f', '--forever', action='store_true', help='forever, watch forever, default: False')
        parser.add_argument('-i', '--interval', type=int, help='interval', default=2)
        parser.add_argument('-l', '--columns', type=str, help='columns, control output columns, default: *', default='*')
        parser.add_argument('-t', '--trigger', type=str, help='trigger, trigger to watch, default: *', default='*')
        parser.add_argument('-r', '--receiver', type=str, help='receiver, receiver to watch, default: dingtalk',
                            default='dingtalk')

    @staticmethod
    def watch_forever(data_source: DataSource, stocks, interval=2, columns='*', trigger='*', receiver='dingtalk'):
        now = datetime.now()
        am_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
        am_close_time = now.replace(hour=11, minute=30, second=0, microsecond=0)
        pm_open_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
        pm_close_time = now.replace(hour=15, minute=0, second=0, microsecond=0)
        histories: Dict[str, List] = {}
        if trigger == '*':
            triggers = Trigger.values()
        else:
            triggers = []
            for t in trigger.split(','):
                t = t.strip()
                if t not in Trigger:
                    raise ValueError(f"trigger {t} not found")
                triggers.append(Trigger[t])
        if receiver:
            try:
                receiver = Receiver[receiver]
            except KeyError:
                raise ValueError(f"receiver {receiver} not found")
        print("Start watching, %s triggers selected, press Ctrl+C to stop" % (len(triggers),))
        if now < am_open_time:
            print("Market is not open yet, waiting for open...")
            time.sleep((am_open_time - now).seconds)
            now = datetime.now()
        try:
            while now < pm_close_time:
                if am_close_time < now < pm_open_time:
                    print("Market is sleeping, waiting for next open...")
                    time.sleep((pm_open_time - now).seconds)
                    now = datetime.now()
                for stock in stocks:
                    kline = data_source.request_kline(stock, date=now)
                    stock_histories = histories.setdefault(stock.code, [])
                    if len(stock_histories) > 0:
                        last = stock_histories[-1]
                        if last.current != kline.current:
                            for trigger in triggers:
                                trigger: BaseTrigger
                                trigger.trigger(kline, stock_histories)
                    stock_histories.append(kline)
                    print(kline.info(columns))
                time.sleep(interval)
                now = datetime.now()
        except KeyboardInterrupt:
            print("Stop watching, Bye")
        else:
            print("Market closed, Stop watching")

    def handle(self, *args, **options):
        code = options['code']
        name = options['name']
        date = options['date']
        if date:
            date = datetime.strptime(date, '%Y-%m-%d')
        if not code and not name:
            return self.print_help(sys.argv[0], subcommand='kline_watcher')
        stocks = [StockItem(code=x.strip() if x else None, name=y.strip() if y else None)
                  for x, y in zip_longest(code.split(','), name.split(','))]
        data_source = DataSource(data_source=options['data_source'], proxies=self.proxies, is_registry=False)
        if options['forever']:
            self.watch_forever(data_source, stocks, interval=options['interval'], columns=options['columns'])
        else:
            for stock in stocks:
                kline = data_source.request_kline(stock, date=date)
                print(kline.info(options['columns']))

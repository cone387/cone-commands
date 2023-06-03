from cone.utils.classes import ClassManager
from cone.utils.functional import classproperty
from typing import List
import json


DataSource = ClassManager(path='cone_commands.contrib.stock.data_source', name='DataSourceManager',
                          unique_keys=['data_source'])

Trigger = ClassManager(path='cone_commands.contrib.stock.trigger', name='TriggerManager',
                       unique_keys=['trigger'])

Receiver = ClassManager(path='cone_commands.contrib.stock.receiver', name='ReceiverManager',
                        unique_keys=['receiver'])


def get_code_by_name(name):
    return name


def get_name_by_code(code):
    return code


class StockItem:

    def __init__(self, code=None, name=None):
        assert code or name, "code or name must be provided"
        if not code:
            code = get_name_by_code(name)
        if not name:
            name = get_code_by_name(code)
        self.code = code
        self.name = name

    def __hash__(self):
        return hash(self.code)

    def __str__(self):
        return self.name

    __repr__ = __str__


class KLine:
    def __init__(self, stock, date, open_price, max_price, min_price, current_price, diff, change):
        self.stock = stock
        self.date = date
        self.open = open_price
        self.max = max_price
        self.min = min_price
        self.current = current_price
        self.diff = diff
        self.change = change

    def info(self, columns='*'):
        if columns == '*':
            columns = [x for x in self.__dict__ if not x.startswith('_')]
        else:
            columns = [x.strip() for x in columns.split(',')]
        return {k: v for k, v in self.__dict__.items() if k in columns}

    def __str__(self):
        return json.dumps(
            {
                'date': self.date.strftime('%Y-%m-%d'),
                'open': self.open,
                'max': self.max,
                'min': self.min,
                'current': self.current,
                'diff': self.diff,
                'change': self.change,
            }
        )

    def __repr__(self):
        return "<%s,%s>" % (self.stock.name, self.change)


class BaseDataSource:
    name = None

    def __init__(self, proxies=None):
        self.proxies = proxies

    @classproperty
    def data_source(cls):
        return cls.name or cls.__module__.split(".")[-1]

    @data_source.setter
    def data_source(cls, value):
        cls.name = value

    def request_kline(self, stock: StockItem, date=None) -> KLine:
        raise NotImplementedError


class BaseReceiver:
    name = None

    @classproperty
    def receiver_name(cls):
        return cls.name or cls.__module__.split(".")[-1]

    @receiver_name.setter
    def receiver_name(cls, value):
        cls.name = value

    def on_received(self, trigger, current: KLine, histories: List[KLine]):
        raise NotImplementedError


class BaseTrigger:
    name = None
    receiver = None

    @classproperty
    def trigger_name(cls):
        return cls.name or cls.__module__.split(".")[-1]

    @trigger_name.setter
    def trigger_name(cls, value):
        cls.name = value

    def trigger(self, current: KLine, histories: List[KLine]):
        if self.triggerable(current, histories):
            self.on_triggered(current, histories)

    def triggerable(self, current, histories) -> bool:
        raise NotImplementedError

    def on_triggered(self, current: KLine, histories: List[KLine]):
        if self.receiver:
            try:
                receiver: BaseReceiver = Receiver[self.receiver]
            except KeyError:
                raise ValueError("receiver %s not found" % self.receiver)
            receiver.on_received(self, current, histories)

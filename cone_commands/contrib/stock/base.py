from cone.utils.classes import ClassManager
from cone.utils.functional import classproperty
import os


DataSource = ClassManager(path='cone_commands.contrib.stock.data_source', name='DataSourceManager',
                          unique_keys=['data_source'])


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


class BaseDataSource:
    name = None

    @classproperty
    def data_source(cls):
        return cls.__module__.split(".")[-1]

    @data_source.setter
    def data_source(cls, value):
        cls.name = value

    def request_kline(self, stock: StockItem, date=None):
        raise NotImplementedError

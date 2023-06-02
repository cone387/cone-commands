from datetime import datetime
from ..base import StockItem, DataSource, BaseDataSource, KLine
import requests

home_url = 'https://xueqiu.com/hq'
url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json'


headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/98.0.4758.80 Safari/537.36'
}


def print_red(text):
    print(f"\033[31m{text}\033[0m")


def print_green(text):
    print(f"\033[32m{text}\033[0m")


def get_cookies():
    response = requests.get(home_url, headers=headers)
    token = response.cookies.get('xq_a_token')
    assert token, "xq_a_token not found"
    return {'xq_a_token': token}


@DataSource.register()
class XueQiuDataSource(BaseDataSource):

    def __init__(self, proxy=None):
        self._cookies = None
        super(XueQiuDataSource, self).__init__(proxy=proxy)

    @property
    def cookies(self):
        if not self._cookies:
            self._cookies = get_cookies()
        return self._cookies

    def request_kline(self, stock: StockItem, date: datetime = None):
        date = date or datetime.now()
        params = {
            "symbol": stock.code,
            "begin": int(datetime(date.year, date.month, date.day).timestamp() * 1000),
            "end": int(datetime(date.year, date.month, date.day, 15).timestamp() * 1000),
            "period": "day",
            "type": "before",
            "indicator": "kline"
        }
        error = None
        for i in range(3):
            try:
                response = requests.get(url, params=params, headers=headers, cookies=self.cookies, verify=False,
                                        proxies=self.proxies)
            except Exception as e:
                error = e
                break
            try:
                item = response.json()['data']['item']
                _, _, open_price, max_price, min_price, current_price, diff, change, *_ = item[0]
            except IndexError:
                self._cookies = None
                continue
            except KeyError as e:
                print_red(response.json())
                error = e
                break
            except Exception as e:
                error = e
                break
            return KLine(stock, date, open_price, max_price, min_price, current_price, diff, change)
        raise Exception(f"request_kline failed, code: {stock.code}, date: {date}, "
                        f"proxies: {self.proxies} error: {error}")

from datetime import datetime
from ..base import StockItem, DataSource, BaseDataSource
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
    print(token)
    return {'xq_a_token': token}


@DataSource.register()
class XueQiuDataSource(BaseDataSource):

    def __init__(self):
        self._cookies = get_cookies()
        super(XueQiuDataSource, self).__init__()

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
        for i in range(3):
            response = requests.get(url, params=params, headers=headers, cookies=cookies)
            try:
                item = response.json()['data']['item']
                _, _, open_price, max_price, min_price, current_price, diff, change, *_ = item[0]
            except:
                print_red(response.text)
                continue
            return {
                'date': date,
                'open': open_price,
                'max': max_price,
                'min': min_price,
                'current': current_price,
                'diff': diff,
                'change': change,
            }
        raise Exception(f"request_kline failed, code: {stock.code}, date: {date}")
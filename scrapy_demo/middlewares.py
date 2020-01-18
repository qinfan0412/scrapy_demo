import hashlib
import time

from scrapy import Spider, Request
from scrapy.http import Response


class MayiProxyMiddleware:

    def process_request(self, request: Request, spider: Spider):
        if 'no_proxy' in request.meta:
            return None

        request.meta['proxy'] = 'http://s1.proxy.mayidaili.com:8123'
        auth_header = self._get_mayi_auth_header()
        request.headers['Mayi-Authorization'] = auth_header
        return None

    @staticmethod
    def _get_mayi_auth_header(start_transaction: bool = None,
                              hold_transaction: bool = None):
        app_key = "197016351"
        app_secret = "1405987d51e35dae7105e0b941b12409"

        parmas = {
            'app_key': app_key,
            'timestamp': time.strftime(r'%Y-%m-%d %H:%M:%S'),
        }

        if start_transaction:
            # A transaction max hold 30s
            print('start_transaction')
            parmas['release-transaction'] = '1'
            parmas['with-transaction'] = '1'

        if hold_transaction:
            print('hold_transaction')
            parmas['with-transaction'] = '1'

        codes = app_secret
        for k, v in sorted(parmas.items(), key=lambda x: x[0]):
            codes += k + v
        codes += app_secret
        sign = hashlib.md5(codes.encode('utf-8')).hexdigest().upper()

        proxy_auth_header = 'MYH-AUTH-MD5 sign=' + sign
        for k, v in parmas.items():
            proxy_auth_header += '&' + k + '=' + v

        return proxy_auth_header

    def process_response(self, request: Request, response: Response, spider: Spider):
        if 'no_proxy' in request.meta:
            return response

        if response.status in (407, 429):
            spider.logger.error('Response status code is {}. Response text: {}. Requests headers: {}'.format(
                response.status, response.text, request.headers))
        return response

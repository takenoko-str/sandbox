import os
import warnings
import requests
import unittest
from db import WAF
from bot import Bot
from backoff import backoff
import time


@backoff
def get_own_host():
    headers = {'User-Agent': 'curl'}
    ip = requests.get('https://ifconfig.io', headers=headers).text.strip('\n')
    return ip


class TestRequest(unittest.TestCase):

    @backoff
    def test_ua_is_google_bot(self):
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        status = 403
        res = requests.get(self.url, headers=headers)
        self.assertEqual(status, res.status_code)

    @backoff
    def test_ua_not_google_bot(self):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                 " (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
        status = 200
        res = requests.get(self.url, headers=headers)

        self.assertEqual(status, res.status_code)

    def setUp(self):
        warnings.filterwarnings("ignore",
                                category=ResourceWarning,
                                message="unclosed.*<ssl.SSLSocket.*>")
        ip = get_own_host()
        self.waf = WAF.alb()
        self.bot = Bot(ip, None, None)
        self.waf.deny(self.bot)
        self.url = os.getenv('ALB_DOMAIN')
        time.sleep(3)

    def tearDown(self):
        self.waf.allow(self.bot)


if __name__ == '__main__':
    unittest.main()

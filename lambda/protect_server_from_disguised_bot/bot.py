import socket
import re


class Bot:

    def __init__(self, ip, useragent, domain):
        self.ip = ip
        self.useragent = useragent
        self.domain = domain

    @classmethod
    def from_log(cls, log):
        return cls(
            log.useragent(),
            log.ip(),
            None
        )

    def named_googlebot(self):
        return 'Googlebot' == self.useragent

    @staticmethod
    def is_google_domain(domain):
        pattern = r'(([a-z0-9-]+\.*)+)\.google(bot)?.com'
        return re.match(pattern, domain)

    def reverse_lookup(self):
        try:
            self.domain = socket.gethostbyaddr(self.ip)[0]
            return self.domain
        except Exception as e:
            return

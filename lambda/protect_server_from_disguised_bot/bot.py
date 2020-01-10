import socket
import re

class Bot:

    def __init__(self, ip, useragent):
        self.ip = ip
        self.useragent = useragent

    @classmethod
    def from_log(cls, log):
        return cls(
            log.useragent(),
            log.ip()
        )

    def named_googlebot(self):
        return 'Googlebot' == self.useragent

    def is_google_domain(self, domain):
        pattern = r'(([a-z0-9-]+\.*)+)\.google(bot)?.com'
        return re.match(pattern, domain)

    def reverse_lookup(self):
        try:
            return socket.gethostbyaddr(self.ip)[0]
        except:
            return False

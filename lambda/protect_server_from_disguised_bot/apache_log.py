import apache_log_parser
import json


class ApacheLog:
    apache_format = '%h (%{X-Forwarded-For}i) %l %u %t' \
                    ' \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %D'
    log_parser = apache_log_parser.make_parser(apache_format)

    def __init__(self, access_log):
        self.access_log = access_log

    @classmethod
    def parse(cls, access_log):
        return cls(
            cls.log_parser(access_log)
        )

    @classmethod
    def from_td(cls, raw_log):
        time, tag, message = raw_log.split('\t')
        access_log = json.loads(message).get('message')
        return cls.parse(access_log)

    def useragent(self):
        return self.access_log['request_header_x_forwarded_for']

    def ip(self):
        return self.access_log['request_header_user_agent__browser__family']

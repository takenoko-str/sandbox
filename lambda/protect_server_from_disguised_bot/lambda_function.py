import re, socket
import apache_log_parser
import logging
import boto3
import math, time
import urllib.parse
import os
import json
import io, gzip
from datetime import datetime
import enum
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Bot:

    def __init__(self, ip, useragent):
        self.ip = ip
        self.useragent = useragent

    @classmethod
    def set(cls, log):
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


class WAF:
    # AWS WAF Classic
    def __init__(self, client, ip_set_id, bot):
        self.client = client
        self.id = resource_id
        self.bot = bot

    @classmethod
    def alb(cls, bot):
        session = boto3.session.Session(region_name=os.getenv('AWS_REGION'))
        waf_regional = session.client('waf-regional')
        return cls(waf_regional, os.getenv('ALB_IP_SET_ID'), bot)

    @classmethod
    def cloudfront(cls, bot):
        waf = boto3.client('waf')
        return cls(waf, os.getenv('CF_IP_SET_ID'), bot)

    @backoff
    def ban(self):
        self.client.update_ip_set(IPSetId=self.ip_set_id,
            ChangeToken=self.client.get_change_token()['ChangeToken'],
            Updates=[{
                'Action': 'INSERT',
                'IPSetDescriptor': {
                    'Type': 'IPV4',
                    'Value': self.bot.ip + "/32"
                }
            }]
        )


class NACL:
    def __init__(self, nacl, bot):
        self.nacl = nacl
        self.bot = bot

    @classmethod
    def set(cls, bot):
        ec2 = boto3.resource('ec2')
        nacl = ec2.NetworkAcl(os.getenv('NACL_ID'))
        return cls(nacl, bot)

    def ban(self, rule_no):
        self.nacl.create_entry(
            CidrBlock=self.bot.ip + '/32',
            Egress=False,
            PortRange={
                'From': 0,
                'To': 65535
            },
            Protocol='-1',
            RuleAction='deny',
            RuleNumber=rule_no
        )


class DynamoDB:
    def __init__(self, bot):
        self.table_name = os.getenv('DDB_IP_TABLE_NAME')
        self.client = boto3.client('dynamodb')
        self.bot = bot

    def insert(self, status):
        # ISO 8601
        utc_now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        item = {
            'ip': {'S': self.bot.ip},
            'timestamp': {'S': utc_now}, 
            'status': {'S': status}
        }
        self.client.put_item(TableName=self.table_name, Item=item)


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


class S3:
    def __init__(self, bucket):
        self.client = boto3.client("s3")
        self.bucket = bucket

    def get_body(self, filename):
        try:
            res = self.client.get_object(Bucket=self.bucket, Key=filename)
            with gzip.open(io.BytesIO(res['Body'].read()), 'rt') as f:
                return f.read().splitlines()
        except Exception as e:
            return logger.error("Failed to get uploaded file: {}".format(e))

    @classmethod
    def from_trigger(cls, event):
        bucket = event['Records'][0]['s3']['bucket']['name']
        filename = urllib.parse.unquote_plus(
            event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        return cls(bucket).get_body(filename)


def lambda_handler(event, context):
    logger.info("now loading")
    access_logs = S3.from_trigger(event)
    
    for raw in access_logs:
        apache_log = ApacheLog.from_td(raw)
        bot = Bot.set(apache_log)
        ddb = DynamoDB(bot)
    
        if not bot.named_googlebot():
            logging.info("ユーザエージェントが違います")
            continue
    
        reverse_domain = bot.reverse_lookup()
        if not reverse_domain:
            ddb.insert('BAN')
            logging.warning("逆引きできないIPがGoogleBotを名乗っています")
            continue
    
        if bot.is_google_domain(reverse_domain):
            ddb.insert('PASS')
            logging.info("GoogleBotです")
        else:
            ddb.insert('BAN')
            logging.info("このドメインはGoogleBotではありません")

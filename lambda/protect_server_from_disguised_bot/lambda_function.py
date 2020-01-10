import logging
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from backoff import backoff
from apache_log import ApacheLog
from s3 import S3
from bot import Bot
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class WAF:
    # AWS WAF Classic
    def __init__(self, client, ip_set_id):
        self.client = client
        self.ip_set_id = ip_set_id

    @classmethod
    def alb(cls):
        session = boto3.session.Session(region_name=os.getenv('AWS_REGION'))
        waf_regional = session.client('waf-regional')
        return cls(waf_regional, os.getenv('ALB_IP_SET_ID'))

    @classmethod
    def cloudfront(cls):
        waf = boto3.client('waf')
        return cls(waf, os.getenv('CF_IP_SET_ID'))

    @backoff
    def deny(self, bot):
        self.client.update_ip_set(
            IPSetId=self.ip_set_id,
            ChangeToken=self.client.get_change_token()['ChangeToken'],
            Updates=[{
                'Action': 'INSERT',
                'IPSetDescriptor': {
                    'Type': 'IPV4',
                    'Value': bot.ip + "/32"
                }
            }]
        )


class NetACL:
    def __init__(self, net_acl):
        self.net_acl = net_acl

    @classmethod
    def set(cls):
        ec2 = boto3.resource('ec2')
        net_acl = ec2.NetworkAcl(os.getenv('NACL_ID'))
        return cls(net_acl)

    def id(self):
        return self.net_acl.id
        
    def deny(self, bot, ddb):
        if ddb.exist(bot):
            return
        try:
            self.net_acl.create_entry(
                CidrBlock=bot.ip + '/32',
                Egress=False,
                PortRange={
                    'From': 0,
                    'To': 65535
                },
                Protocol='-1',
                RuleAction='deny',
                RuleNumber=ddb.max_rule_no + 1
            )
        except Exception as e:
            return False
        else:
            ddb.deny(bot)


class DynamoDB:
    def __init__(self, net_acl):
        self.ddb = boto3.resource('dynamodb')
        self.table = self.ddb.Table(os.getenv('DDB_IP_TABLE_NAME'))
        self.net_acl = net_acl
        items = self.table.query(
            KeyConditionExpression=Key('network_acl_id').eq(self.net_acl.id()),
            FilterExpression=Attr('status').eq('DENY')
        )['Items']
        if len(items) > 0:
            self.max_rule_no = int(max(items, key=lambda x: int(x.get('rule_no', 0))).get('rule_no', 0))
        else:
            self.max_rule_no = 0

    def exist(self, bot):
        items = self.table.query(
            KeyConditionExpression=Key('network_acl_id').eq(self.net_acl.id()) & Key('ip').eq(bot.ip)
        )['Items']
        return len(items) > 0

    def deny(self, bot):
        # ISO 8601
        utc_now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        self.max_rule_no += 1
        item = {
            'network_acl_id': self.net_acl.id(),
            'ip': bot.ip,
            'timestamp': utc_now, 
            'status': 'DENY',
            'rule_no': str(self.max_rule_no),
        }
        self.table.put_item(Item=item)

    def allow(self, bot):
        # ISO 8601
        utc_now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        item = {
            'network_acl_id': 'NULL',
            'ip': bot.ip,
            'timestamp': utc_now, 
            'status': 'ALLOW',
        }
        self.table.put_item(Item=item)


def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)
    access_logs = S3.from_trigger(event)
    net_acl = NetACL.set()
    ddb = DynamoDB(net_acl)
    waf = WAF.alb()
    for raw in access_logs:
        apache_log = ApacheLog.from_td(raw)
        bot = Bot.from_log(apache_log)

        if not bot.named_googlebot():
            logger.info("ユーザエージェントが違います")
            continue

        reverse_domain = bot.reverse_lookup()
        if not reverse_domain:
            net_acl.deny(bot, ddb)
            waf.deny(bot)
            logger.warning("逆引きできないIPがGoogleBotを名乗っています")
            continue

        if bot.is_google_domain(reverse_domain):
            ddb.allow(bot)
            logger.info("GoogleBotです")
        else:
            net_acl.deny(bot, ddb)
            waf.deny(bot)
            logger.info("このドメインはGoogleBotではありません")

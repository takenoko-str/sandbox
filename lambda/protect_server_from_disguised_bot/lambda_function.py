import logging
import os
from apache_log import ApacheLog
from s3 import S3
from bot import Bot
from db import WAF
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)
    access_logs = S3.from_trigger(event)
    waf = WAF.alb()
    for raw in access_logs:
        apache_log = ApacheLog.from_td(raw)
        bot = Bot.from_log(apache_log)

        if not bot.named_googlebot():
            logger.info("ユーザエージェントが違います")
            continue

        if not bot.reverse_lookup():
            waf.deny(bot)
            logger.warning("逆引きできないIPがGoogleBotを名乗っています")
            continue

        if not bot.is_google_domain():
            waf.deny(bot)
            logger.info("このドメインはGoogleBotではありません")


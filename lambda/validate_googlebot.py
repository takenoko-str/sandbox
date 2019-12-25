import re, socket
import apache_log_parser
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
logger.addHandler(sh)


def reverse_lookup(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return False


def valid_googlebot(domain):
    pattern = '(([a-z0-9-]+\.*)+)\.google(bot)?.com'
    return re.match(pattern, domain)


def parse_access_log(line):
    pattern = '%h (%{X-Forwarded-For}i) %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %D'
    return apache_log_parser.make_parser(pattern)(line)


def named_googlebot(useragent):
    return 'Googlebot' == useragent


if __name__ == '__main__':
    white_table, black_table = [], []
    
    with open('access_log', 'r') as f:
        access_logs = f.read().splitlines()
    
    for line in access_logs:
        access_log = parse_access_log(line)
        ip = access_log['request_header_x_forwarded_for']
        useragent = access_log['request_header_user_agent__browser__family']
    
        if not named_googlebot(useragent):
            logging.debug("ユーザエージェントが違います")
            continue
    
        reverse_domain = reverse_lookup(ip)
        if not reverse_domain:
            black_table.append(ip)
            logging.warning("逆引きできないIPがGoogleBotを名乗っています")
            continue
    
        bot_domain = valid_googlebot(reverse_domain)
        if bot_domain:
            white_table.append(ip)
            logging.info("GoogleBotです")
    
        if not bot_domain:
            black_table.append(ip)
            logging.info("このドメインはGoogleBotではありません")
    
    logging.info(f"white list: {white_table}")
    logging.info(f"black list: {black_table}")
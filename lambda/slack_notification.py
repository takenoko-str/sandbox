import boto3
import json
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import boto3

SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
HOOK_URL = os.getenv('HOOK_URL')
GROUP_NAME = os.getenv('GROUP_NAME')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))

    logs = boto3.client('logs')
    response = logs.describe_log_streams(
        logGroupName=GROUP_NAME,
        orderBy='LastEventTime',
        descending=True,
        limit=1
    )
    
    streams = response.get('logStreams')
    stream_name = streams[0].get('logStreamName')
    response = logs.filter_log_events(
        logGroupName=GROUP_NAME,
        logStreamNames=[stream_name],
        filterPattern="error",
    )
    
    latest_event = response['events'][-1]
    slack_message = {
        'channel': SLACK_CHANNEL,
        'text': "{} {} {}".format(GROUP_NAME, latest_event.get("timestamp"), latest_event.get("message"))
    }
    
    req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
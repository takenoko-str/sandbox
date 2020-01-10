import boto3
import gzip
import io
import urllib.parse
from logging import getLogger, INFO, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())
logger.setLevel(INFO)
logger.propagate = True


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
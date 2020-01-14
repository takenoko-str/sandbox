import math
import time
from logging import getLogger, INFO, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())
logger.setLevel(INFO)
logger.propagate = True

API_CALL_NUM_RETRIES = 2


# original retrying module
def backoff(func):
    def wrapper(*args, **kwargs):
        for attempt in range(API_CALL_NUM_RETRIES):
            try:
                logger.info("Trying...")
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(e)
                delay = math.pow(2, attempt)
                logger.info("Retrying in %d seconds..." % delay)
                time.sleep(delay)
            else:
                break
        else:
            logger.info("Failed ALL attempts to call API")
    return wrapper


@backoff
def echo():
    raise ValueError("error!")


if __name__ == '__main__':
    echo()

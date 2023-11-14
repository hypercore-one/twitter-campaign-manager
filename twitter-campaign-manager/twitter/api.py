import requests
from enum import StrEnum

from config.config import Config
from utils.logger import init_logger


class Endpoints(StrEnum):
    BASE = "https://api.twitter.com/2",
    SEARCH_RECENT = f'{BASE[0]}/tweets/search/recent',
    TWEETS = f'{BASE[0]}/tweets'
    USERS = f'{BASE[0]}/users'


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {Config.TWITTER_BEARER_TOKEN}"
    r.headers['User-Agent'] = "ZenonNetwork"
    return r


def connect_to_endpoint(url, params):
    logger = init_logger('twitter')
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        logger.error(f'{url} {params} || {response.status_code} {response.text}')
    return response.json()

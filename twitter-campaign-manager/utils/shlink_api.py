# Fetches link clicks for https://znn.link

import requests

from config.config import Config
from utils.logger import init_logger, Logger


def get_url(short_code):
    return f"https://znn.link/rest/v3/short-urls/{short_code}/visits"


def get_params(start_time, end_time):
    return {
        'startDate': start_time,
        'endDate': end_time,
        'excludeBots': True
    }


def bearer_oauth(r):
    r.headers["accept"] = "application/json"
    r.headers['X-Api-Key'] = Config.SHLINK_API_KEY
    return r


def connect_to_endpoint(url, params):
    logger = init_logger('shlink')
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        logger.error(f'{url} {params} || {response.status_code} {response.text}')
        return Exception(response.status_code, response.text)
    return response.json()


def twitter_refs(campaign, expanded_url):
    if Config.SHLINK_API_KEY == "":
        Logger.logger.warning('SHLINK API KEY is not set')
        return 0

    twitter = 'https://t.co/'
    twitter_clickthroughs = 0

    short_code = expanded_url.split('/')[-1]
    url = get_url(short_code)
    params = get_params(campaign['start_time'], campaign['end_time'])
    response = connect_to_endpoint(url, params)

    if type(response) == Exception:
        return 0

    for click in response['visits']['data']:
        if click['referer'] == twitter:
            twitter_clickthroughs += 1
    return twitter_clickthroughs

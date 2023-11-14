from enum import IntEnum

from twitter.api import connect_to_endpoint, Endpoints
from twitter.helper import exclude_null_from_dict


class Limits(IntEnum):
    RECENT = 100,  # tweets per request, pagination if over this amount
    RECENT_MAX = 450,  # 450 recent tweets per 15-minute window
    RECENT_COOLDOWN = 15 * 60,
    TWEETS = 100,  # per request
    TWEETS_MAX = 200,  # 200 requests per 15-minute window
    TWEETS_COOLDOWN = 15 * 60,
    USERS = 75,  # per request
    USERS_MAX = 75,  # 75 requests per 15-minute window
    USERS_COOLDOWN = 15 * 60


def get_recent_posts(start_time=None, end_time=None, since_id=None, query='#ZenonNetwork',
                     max_results=Limits.RECENT.value):
    '''
    400 {"errors":[{"parameters":{"since_id":["1721361432158114055"],"end_time":["2023-11-07T00:00Z"]},
        "message":"Invalid use of 'since_id' or 'until_id' in conjunction with 'start_time' or 'end_time'."}]
    '''
    return connect_to_endpoint(Endpoints.SEARCH_RECENT, exclude_null_from_dict({
        'query': query,
        # 'since_id': since_id,
        'start_time': start_time,
        'end_time': end_time,
        'max_results': max_results,
        'tweet.fields': 'public_metrics,author_id,created_at,entities',
        'user.fields': 'username,name,public_metrics,verified',
        'expansions': 'author_id',
    }))


def get_post(post_id):
    response = connect_to_endpoint(Endpoints.TWEETS, {
        'ids': post_id,
        'tweet.fields': 'public_metrics,author_id,created_at,entities'
    })
    return response['data']


def get_user(user_id):
    response = connect_to_endpoint(Endpoints.USERS, {
        'ids': user_id,
        'user.fields': 'public_metrics,id,created_at,name,description,protected,username,verified,verified_type,'
                       'withheld,url,entities'
    })
    return response['data']

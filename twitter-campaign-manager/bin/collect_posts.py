from datetime import datetime, timedelta
from time import sleep

from database.queries.get_queries import get_all_values, get_last_post_time
from database.queries.update_queries import insert_posts, insert_users
from database.tables import Table
from twitter.helper import format_twitter_query
from utils.campaign import get_active_campaign, is_campaign_over
from utils.logger import Logger

from twitter.queries import get_recent_posts, Limits
from utils.scores import calculate_post_scores


def filter_retweets(posts):
    result = []
    for p in posts:
        if p['text'][0:2] != 'RT':
            result.append(p)
    return result


def update_db(twitter_response):
    posts = twitter_response
    users = twitter_response['includes']['users']

    weights = get_all_values(Table.WEIGHTS)
    posts = filter_retweets(posts['data'])
    posts = calculate_post_scores(posts, weights)
    insert_posts(posts)
    insert_users(users)


def collect_new_posts():
    campaign = get_active_campaign()
    campaign_finished = is_campaign_over(campaign['end_time'])
    if campaign_finished:
        end_time = campaign['end_time']
    else:
        end_time = None

    fetched_all_tweets = False
    fetch_counter = 0
    while not fetched_all_tweets:
        db_response = get_last_post_time()
        if db_response is not None:
            start_time = (datetime.fromisoformat(db_response) + timedelta(seconds=1)).isoformat()
        else:
            start_time = campaign['start_time']

        if Limits.RECENT_MAX.value - fetch_counter >= Limits.RECENT.value:
            max_limit = Limits.RECENT.value
        else:
            max_limit = Limits.RECENT_MAX.value - fetch_counter

        twitter_response = get_recent_posts(
            start_time=start_time,
            end_time=end_time,
            query=format_twitter_query(campaign['post_criteria']),
            max_results=max_limit,
        )

        fetched_count = twitter_response['meta']['result_count']
        if fetched_count != 0:
            fetch_counter += fetched_count
            update_db(twitter_response)

        if fetched_count < Limits.RECENT_MAX.value:
            Logger.logger.info(f'Fetched {fetched_count} tweets')
            return

        if fetch_counter >= Limits.RECENT_MAX.value:
            sleep(Limits.RECENT_COOLDOWN.value)
            fetch_counter = 0


if __name__ == '__main__':
    collect_new_posts()

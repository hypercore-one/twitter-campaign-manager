from enum import StrEnum
from time import sleep

from database.queries.delete_queries import delete_data, delete_inactive_users
from database.queries.get_queries import get_ids, get_unique_active_poster_ids, get_all_values
from database.queries.update_queries import insert_posts, insert_users
from database.tables import Table
from utils.logger import Logger

from twitter.queries import get_post, Limits, get_user
from utils.twitter import check_deleted_posts, extract_post_urls, extract_profile_url
from utils.scores import calculate_post_scores, calculate_user_multipliers, calculate_user_scores


class DataType(StrEnum):
    POST = 'posts',
    USER = 'users'


def update_data(data_type):
    """
    1. Fetches a list of user or post IDs from the db
    2. Queries Twitter for the latest data related to those IDs
    3. Updates the db
    """
    data_type = data_type.value
    if data_type == DataType.POST:
        ids = get_ids(Table.POSTS)
        limit = Limits.TWEETS  # per request
        max = Limits.TWEETS_MAX
        cooldown = Limits.TWEETS_COOLDOWN.value
    elif data_type == DataType.USER:
        ids = get_unique_active_poster_ids()
        limit = Limits.USERS  # per request
        max = Limits.USERS_MAX
        cooldown = Limits.USERS_COOLDOWN.value
    else:
        Logger.logger.error('update_data({type.value}): invalid type')
        return

    if len(ids) == 0:
        Logger.logger.warning(f'No active (score > 0) {data_type} for the current campaign')
        delete_inactive_users()
        return

    loops = 1
    if len(ids) > limit:
        loops += len(ids) // limit

    data = []
    index_start = 0
    index_end = 0
    fetch_counter = 0

    Logger.logger.info(f'update_data({data_type}): retrieving {len(ids)} {data_type}')
    for i in range(loops):

        if i == loops - 1:
            index_end = len(ids)
        else:
            index_end += limit

        fetch_counter += len(ids[index_start:index_end])

        api_id_param = ''
        for id in ids[index_start:index_end]:
            api_id_param += f"{id},"

        try:
            if data_type == DataType.POST:
                result = get_post(api_id_param[:-1])
            if data_type == DataType.USER:
                result = get_user(api_id_param[:-1])

            for v in result:
                data.append(v)
        except Exception as e:
            Logger.logger.error(f'update_data({data_type}): {api_id_param} || {e}')

        if i != loops - 1:
            index_start += limit
            if max - fetch_counter == 0:
                fetch_counter = 0
                print(f'Twitter fetch cooldown: {cooldown} seconds...')
                sleep(cooldown)

    if len(data) > 0:
        if data_type == DataType.POST:
            deleted_post_ids = check_deleted_posts(ids, data)
            delete_data(deleted_post_ids, Table.POSTS) if len(deleted_post_ids) > 0 else None

        weights = get_all_values(Table.WEIGHTS)

        if data_type == DataType.POST:
            data = extract_post_urls(data)
            data = calculate_post_scores(data, weights)
            insert_posts(data)
        if data_type == DataType.USER:
            data = extract_profile_url(data)
            data = calculate_user_multipliers(data, weights)
            data = calculate_user_scores(data)
            insert_users(data)
            delete_inactive_users()
    else:
        Logger.logger.error(f"update_data({data_type}): expected {len(ids)}, received none from Twitter")


if __name__ == '__main__':
    update_data(DataType.POST)
    update_data(DataType.USER)

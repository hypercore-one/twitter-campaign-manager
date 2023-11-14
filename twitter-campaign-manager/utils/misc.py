import postgrest
from datetime import datetime
from dateutil.parser import parse


def is_postgres_exception(result):
    return type(result) == postgrest.exceptions.APIError


def get_tags(text, tags):
    result = []
    for t in tags:
        if text.find(t) != -1:
            result.append(t)
    return result


def get_account_age(created_at):
    seconds_per_day = 60 * 60 * 24
    return (datetime.timestamp(datetime.utcnow()) - parse(created_at).timestamp()) / seconds_per_day

def exclude_null_from_dict(dict):
    result = {}
    for key, value in dict.items():
        if value is not None:
            result[key] = value
    return result


def format_twitter_query(post_criteria):
    # improvement: format the query correctly in the campaigns table
    query = ''
    for string in post_criteria:
        query += f'{string} '
    return query[:-1]

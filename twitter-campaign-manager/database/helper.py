def has_data(response):
    if len(response['data']) > 0:
        return True
    else:
        return False


def unpack(response):
    if has_data(response):
        return response['data']
    else:
        return []

from utils.shlink_api import twitter_refs
from utils.campaign import get_active_campaign


# Only applies to single tweet fetch
def is_post_deleted(post):
    if 'errors' in post.keys():
        if post['errors'][0]['title'] == 'Not Found Error':
            return True
    return False


def check_deleted_posts(db_post_ids, twitter_posts):
    deleted = []
    for db_id in db_post_ids:
        found = False
        for post in twitter_posts:
            if int(post['id']) == db_id:
                found = True
                break
        if not found:
            deleted.append(db_id)

    return deleted


def extract_post_urls(posts):
    campaign = get_active_campaign()
    domains = campaign['link_criteria']
    found_domains = []

    result = []
    for p in posts:
        found_urls = []
        found_url = {}
        if 'urls' in p['entities']:
            for url in p['entities']['urls']:
                expanded_url = url['expanded_url']
                unwound_url = url['unwound_url'] if 'unwound_url' in url else None,
                for d in domains:
                    if len(expanded_url.split(d)) > 1 and d not in found_domains:
                        found_domains.append(d)
                        found_url['expanded_url'] = expanded_url
                        found_url['unwound_url'] = unwound_url[0]

                        if d == 'https://znn.link':
                            found_url['clicks'] = twitter_refs(campaign, expanded_url)
                        else:
                            found_url['clicks'] = 0
                        found_urls.append(found_url)
        p['urls'] = found_urls
        result.append(p)
    return result


def extract_profile_url(users):
    result = []
    for u in users:
        if 'url' in u:
            u['profile_url'] = u['entities']['url']['urls'][0]['expanded_url']
        result.append(u)
    return result

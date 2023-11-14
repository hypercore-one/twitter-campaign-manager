from database.queries.get_queries import get_all_values, get_spam_debuff, get_spammer_ids, get_profile_urls
from database.tables import Table
from utils.campaign import get_active_campaign
from utils.misc import get_account_age, get_tags


def get_score(post_value, multiplier, max_score):
    if post_value * multiplier > max_score:
        return 1 + max_score
    else:
        return 1 + (post_value * multiplier)


def calculate_post_scores(posts, weights):
    result = []
    campaign = get_active_campaign()
    post_length_criteria = campaign['post_length_criteria']
    for post in posts:
        score = 0
        met_post_length_criteria = False
        if len(post['text']) >= post_length_criteria:
            met_post_length_criteria = True

        for w in weights:
            if 'post_' not in w['metric']:
                continue

            metric = w['metric'][w['metric'].find('_') + 1:]
            threshold = w['threshold']
            multiplier = w['multiplier']
            max_score = w['max']

            if metric == 'impression_count':
                if (post['public_metrics'][metric] < threshold and not met_post_length_criteria) or \
                        post['public_metrics'][metric] == 0:
                    score = 0
                    break
                score += get_score(post['public_metrics'][metric], multiplier, max_score)
            elif metric == 'links':
                if 'urls' in post and len(post['urls']) >= threshold:
                    score += get_score(len(post['urls']), multiplier, max_score)
            elif metric == 'link_clicks':
                if 'urls' in post:
                    for link in post['urls']:
                        if int(link['clicks']) >= threshold:
                            score += get_score(link['clicks'], multiplier, max_score)
            else:
                if post['public_metrics'][metric] >= threshold:
                    score += get_score(post['public_metrics'][metric], multiplier, max_score)
                else:
                    score += 0.5

        post['score'] = score
        result.append(post)
    return result


def calculate_user_multipliers(users, weights):
    campaign = get_active_campaign()
    profile_urls = get_profile_urls()
    result = []
    for user in users:
        user_multiplier = 1

        profile_url = None
        for p in profile_urls:
            if int(p['id']) == int(user['id']):
                profile_url = p['profile_url']

        for w in weights:
            if 'post_' in w['metric']:
                continue

            metric = w['metric']
            threshold = w['threshold']
            multiplier = w['multiplier']
            max = w['max']

            tentative_multiplier = 0
            if metric == 'account_age_days':
                if get_account_age(user['created_at']) > threshold:
                    tentative_multiplier = multiplier
            if metric == 'description_hashtags':
                user['description_hashtags'] = get_tags(user['description'], campaign['profile_hashtags_criteria'])
                if len(user['description_hashtags']) > threshold:
                    tentative_multiplier = multiplier
            if metric == 'description_cashtags':
                user['description_cashtags'] = get_tags(user['description'], campaign['profile_cashtags_criteria'])
                if len(user['description_cashtags']) > threshold:
                    tentative_multiplier = multiplier
            if metric == 'verified_blue':
                if user['verified_type'] == 'blue':
                    tentative_multiplier = multiplier
            if metric == 'verified_business':
                if user['verified_type'] == 'business':
                    tentative_multiplier = multiplier
            if metric == 'verified_government':
                if user['verified_type'] == 'government':
                    tentative_multiplier = multiplier
            if metric == 'protected_account':
                if user['protected']:
                    tentative_multiplier = multiplier
            if metric == 'withheld_countries':
                if 'withheld' in user and len(user['withheld']['country_codes']) > threshold:
                    tentative_multiplier = multiplier * len(user['country_codes'])
            if metric == 'followers_count':
                if user['public_metrics']['followers_count'] > threshold:
                    tentative_multiplier = multiplier * user['public_metrics']['followers_count']
            if metric == 'tweet_count':
                if user['public_metrics']['tweet_count'] > threshold:
                    tentative_multiplier = multiplier * user['public_metrics']['tweet_count']
            if metric == 'profile_url' and profile_url is not None:
                for domain in campaign['link_criteria']:
                    if len(profile_url.split(domain)) > 1:
                        tentative_multiplier = multiplier
            # if metric == 'listed_count':
            #    if user['public_metrics']['listed_count'] > threshold:
            #        user_multiplier += multiplier * user['public_metrics']['listed_count']

            if abs(tentative_multiplier) > abs(max):
                tentative_multiplier = max

            user_multiplier += tentative_multiplier

        user['multiplier'] = user_multiplier
        result.append(user)
    return result


def calculate_user_scores(users):
    posts = get_all_values(Table.POSTS)
    spam = get_spam_debuff()
    spammers = get_spammer_ids()

    result = []
    for user in users:
        score = 0
        for post in posts:
            if post['author_id'] == user['id']:
                score += user['multiplier'] * post['score']

        if int(user['id']) in spammers:
            score *= spam

        user['score'] = round(score)

        if score > 0:
            result.append(user)
    return result

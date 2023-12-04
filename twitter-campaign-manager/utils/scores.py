from database.queries.get_queries import get_all_values, get_spam_debuff, get_spammer_ids, get_profile_urls, \
    get_top_posts
from database.tables import Table
from utils.campaign import get_active_campaign
from utils.misc import get_account_age, get_tags


def get_score(post_value, threshold, multiplier, max_score):
    base_score = 0.5
    if post_value >= threshold:
        if post_value * multiplier > max_score:
            return base_score + max_score
        else:
            return base_score + (post_value * multiplier)
    else:
        return base_score


'''
Scoring rules
- text < post_length_criteria ==> score 0
- impression_count == 0 ==> score 0
- else:
    use a base_score of 0.5 for each metric (7 in total)
'''


def calculate_post_scores(posts, weights):
    result = []
    campaign = get_active_campaign()
    post_length_criteria = campaign['post_length_criteria']
    for post in posts:
        score = 0
        if post['public_metrics']['impression_count'] != 0 and len(post['text']) >= post_length_criteria:
            for w in weights:
                if 'post_' not in w['metric']:
                    continue

                metric = w['metric'][w['metric'].find('_') + 1:]
                threshold = w['threshold']
                multiplier = w['multiplier']
                max_score = w['max']

                if metric == 'links':
                    if 'urls' in post:
                        score += get_score(len(post['urls']), threshold, multiplier, max_score)
                elif metric == 'link_clicks':
                    if 'urls' in post:
                        for link in post['urls']:
                            score += get_score(int(link['clicks']), threshold, multiplier, max_score)
                else:
                    score += get_score(post['public_metrics'][metric], threshold, multiplier, max_score)

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
    spam = get_spam_debuff()
    spammers = get_spammer_ids()

    result = []
    for user in users:
        score = 0
        posts = get_top_posts(user['id'])
        for post in posts:
            score += user['multiplier'] * post['score']

        if int(user['id']) in spammers:
            score *= spam

        user['score'] = round(score)

        if score > 0:
            result.append(user)
    return result

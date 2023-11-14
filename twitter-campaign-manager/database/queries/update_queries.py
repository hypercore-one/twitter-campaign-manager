import json

from postgrest import APIResponse
from database.auth import Supabase
from database.queries.delete_queries import delete_all_data
import database.queries.get_queries
from database.helper import unpack
from database.tables import Table
from utils.logger import Logger


def insert_posts(posts):
    batch_insert = []
    for post in posts:
        batch_insert.append({
            'id': post['id'],
            'created_at': post['created_at'],
            'author_id': post['author_id'],
            'text': post['text'],
            'retweet_count': post['public_metrics']['retweet_count'],
            'reply_count': post['public_metrics']['reply_count'],
            'like_count': post['public_metrics']['like_count'],
            'quote_count': post['public_metrics']['quote_count'],
            'bookmark_count': post['public_metrics']['bookmark_count'],
            'impression_count': post['public_metrics']['impression_count'],
            'score': post['score'] if 'score' in post else None,
            'urls': post['urls'] if 'urls' in post else [],
        })

    try:
        result = json.loads(
            APIResponse.model_dump_json(Supabase.client.table(Table.POSTS).upsert(batch_insert).execute()))
        Logger.logger.info(f"Table: posts || inserted: {len(batch_insert)} posts")
        return result
    except Exception as e:
        Logger.logger.info(f"Table: posts || error: {e}")
        return e


def insert_users(users):
    batch_insert = []
    for user in users:
        batch_insert.append({
            'name': user['name'],
            'id': user['id'],
            'username': user['username'],
            'verified': user['verified'],
            'followers_count': user['public_metrics']['followers_count'],
            'tweet_count': user['public_metrics']['tweet_count'],
            'listed_count': user['public_metrics']['listed_count'],
            'verified_type': user['verified_type'] if 'verified_type' in user else 'none',
            'created_at': user['created_at'] if 'created_at' in user else None,
            'protected': user['protected'] if 'protected' in user else False,
            'description_hashtags': user['description_hashtags'] if 'description_hashtags' in user else [],
            'description_cashtags': user['description_cashtags'] if 'description_cashtags' in user else [],
            'withheld_country_codes': user['withheld_country_codes'] if 'withheld_country_codes' in user else [],
            'profile_url': user['profile_url'] if 'profile_url' in user else None,

            'multiplier': user['multiplier'] if 'multiplier' in user else 1,
            'score': user['score'] if 'score' in user else 0,
        })

    try:
        result = json.loads(
            APIResponse.model_dump_json(Supabase.client.table(Table.USERS).upsert(batch_insert).execute()))
        Logger.logger.info(f"Table: users || inserted: {len(batch_insert)} users")
        return result
    except Exception as e:
        Logger.logger.error(f"Table: users || error: {e}")
        return e


def archive_posts(campaign_id):
    posts = database.queries.get_queries.get_all_values(Table.POSTS)
    batch_insert = []
    for post in posts:
        post['campaign_id'] = campaign_id
        batch_insert.append(post)

    try:
        json.loads(
            APIResponse.model_dump_json(Supabase.client.table(Table.ALL_POSTS).upsert(batch_insert).execute()))
        delete_all_data(Table.POSTS)
        Logger.logger.info(f"Table: posts || archived {len(batch_insert)} posts")
    except Exception as e:
        Logger.logger.error(f"Table: posts || archive error: {e}")
        return e


def archive_users(campaign_id):
    users = database.queries.get_queries.get_all_values(Table.USERS)
    batch_insert = []
    for user in users:
        user['campaign_id'] = campaign_id
        batch_insert.append(user)

    try:
        json.loads(
            APIResponse.model_dump_json(Supabase.client.table(Table.ALL_USERS).upsert(batch_insert).execute()))
        delete_all_data(Table.USERS)
        Logger.logger.info(f"Table: users || archived {len(batch_insert)} users")
    except Exception as e:
        Logger.logger.error(f"Table: users || archive error: {e}")
        return e


def set_raffle_seed(seed, id):
    try:
        result = json.loads(
            APIResponse.model_dump_json(
                Supabase.client.table(Table.CAMPAIGNS).update({'raffle_seed': seed}).eq('id', id).execute()))
        Logger.logger.info(f"Table: campaigns || campaign id: {id} || set raffle seed: {seed}")
        return result
    except Exception as e:
        Logger.logger.error(
            f"Table: campaigns || set_raffle_seed error: {e} || campaign id: {id} || set raffle seed: {seed}")
        return e


def set_raffle_winner(id):
    try:
        result = json.loads(
            APIResponse.model_dump_json(
                Supabase.client.table(Table.USERS).update({'raffle_winner': True}).eq('id', id).execute()))
        Logger.logger.info(f"Table: users || set raffle winner: {id}")
        return result
    except Exception as e:
        Logger.logger.error(
            f"Table: users || set_raffle_winner error: {e} || winner: {id}")
        return e


def set_total_score(id):
    scores = database.queries.get_queries.get_all_scores_current_campaign()
    total_score = 0
    for s in scores:
        total_score += s['score']

    try:
        result = json.loads(
            APIResponse.model_dump_json(
                Supabase.client.table(Table.CAMPAIGNS).update({'total_score': total_score}).eq('id', id).execute()))
        Logger.logger.info(f"Table: campaigns || campaign {id} || set total score: {total_score}")
        return result
    except Exception as e:
        Logger.logger.error(
            f"Table: users || set_raffle_winner error: {e} || campaign {id} || set total score: {total_score}")
        return e


def update_campaign_status(id, active):
    try:
        result = json.loads(
            APIResponse.model_dump_json(
                Supabase.client.table(Table.CAMPAIGNS).update({'active': active}).eq('id', id).execute()))
        Logger.logger.info(f"Table: campaigns || campaign id: {id} || set status to: {active}")
        return result
    except Exception as e:
        Logger.logger.error(
            f"Table: campaigns || update_campaign_status error: {e} || campaign: {id} || status: {active}")
        return e


def set_known_spammers():
    existing_spammers = unpack(json.loads(APIResponse.model_dump_json(
        Supabase.client.table(Table.SPAMMERS).select("id").execute())))

    if len(existing_spammers) == 0:
        return

    potential_spammers = unpack(json.loads(APIResponse.model_dump_json(
        Supabase.client.table(Table.USERS).select("id").eq('spammer', False).execute())))

    spammers = []
    for ps in potential_spammers:
        for es in existing_spammers:
            if es['id'] == ps['id']:
                spammers.append(es['id'])

    if len(spammers) > 0:
        for id in spammers:
            try:
                result = json.loads(
                    APIResponse.model_dump_json(
                        Supabase.client.table(Table.USERS).update({'spammer': True}).eq('id', id).execute()))
                Logger.logger.info(f"Table: users || updating spammer id: {id}")
                return result
            except Exception as e:
                Logger.logger.error(
                    f"Table: users || set_known_spammers error: {e} || id: {id}")

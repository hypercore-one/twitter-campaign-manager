import json

from postgrest import APIResponse

from database.auth import Supabase
from database.helper import has_data, unpack
from database.tables import Table
from database.queries.update_queries import set_known_spammers


def get_all_values(table):
    return unpack(json.loads(APIResponse.model_dump_json(
        Supabase.client.table(table).select("*").execute())))


def get_ids(table):
    response = json.loads(APIResponse.model_dump_json(
        Supabase.client.table(table).select("id").order("id.desc").execute()))
    data = []
    if has_data(response):
        for r in response['data']:
            data.append(r['id'])
    return data


def get_last_post_id():
    response = json.loads(
        APIResponse.model_dump_json(
            Supabase.client.table(Table.POSTS).select("id::text").order("id.desc").limit(1).execute()))
    data = []
    if has_data(response):
        for r in response['data']:
            data.append(r['id'])
    return data[0]


def get_last_post_time():
    response = json.loads(
        APIResponse.model_dump_json(
            Supabase.client.table(Table.POSTS).select("created_at").order("id.desc").limit(1).execute()))
    if len(response['data']) > 0:
        return response['data'][0]['created_at']
    else:
        return None


def get_current_campaign():
    return unpack(json.loads(
        APIResponse.model_dump_json(Supabase.client.table(Table.CAMPAIGNS).select("*").eq("active", True).execute())))


def get_campaign_times():
    return unpack(json.loads(
        APIResponse.model_dump_json(
            Supabase.client.table(Table.CAMPAIGNS).select("id, start_time, end_time").execute())))


def get_profile_urls():
    return unpack(json.loads(
        APIResponse.model_dump_json(
            Supabase.client.table(Table.USERS).select("id, profile_url").execute())))


def get_all_scores_current_campaign():
    return unpack(json.loads(
        APIResponse.model_dump_json(
            Supabase.client.table(Table.USERS).select("score").execute())))


def get_raffle_data(campaign):
    response = json.loads(APIResponse.model_dump_json(
        Supabase.client.table(Table.USERS).select("id,score").gt("score", 0).order("score.desc").execute()))

    raffle_eligibility = int(campaign['raffle_eligibility'])
    if len(response['data']) > raffle_eligibility:
        return response['data'][raffle_eligibility:]
    else:
        return []


def get_unique_active_poster_ids():
    response = json.loads(APIResponse.model_dump_json(
        Supabase.client.table(Table.POSTS).select("author_id").gt("score", 0).execute()))
    data = []
    if has_data(response):
        for r in response['data']:
            data.append(r['author_id'])
        data = list(set(data))
    return data


def get_spammer_ids():
    set_known_spammers()

    response = json.loads(APIResponse.model_dump_json(
        Supabase.client.table(Table.USERS).select("id").eq('spammer', True).execute()))
    data = []
    for r in response['data']:
        data.append(r['id'])
    return data


def get_spam_debuff():
    response = json.loads(APIResponse.model_dump_json(
        Supabase.client.table(Table.WEIGHTS).select("multiplier").eq('metric', 'spam_debuff').execute()))
    return response['data'][0]['multiplier']

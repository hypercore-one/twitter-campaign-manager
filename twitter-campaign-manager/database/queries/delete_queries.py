import json

from postgrest import APIResponse

from database.auth import Supabase
from database.helper import unpack
import database.queries.get_queries
from database.tables import Table
from utils.logger import Logger


def delete_data(ids, table):
    for id in ids:
        try:
            json.loads(
                APIResponse.model_dump_json(Supabase.client.table(table).delete().eq('id', id).execute()))
        except Exception as e:
            Logger.logger.error(f"Table: {table} || delete_data failed: {e}")
    Logger.logger.info(f"Table: {table} || deleted: {ids}")


def delete_inactive_users():
    to_delete = []
    inactive = unpack(json.loads(APIResponse.model_dump_json(
        Supabase.client.table(Table.USERS).select("id").eq("score", 0).execute())))
    for user in inactive:
        to_delete.append(user['id'])

    active = database.queries.get_queries.get_unique_active_poster_ids()
    known_users = database.queries.get_queries.get_ids(Table.USERS)
    for user in known_users:
        if str(user) not in active:
            to_delete.append(user)
    delete_data(to_delete, Table.USERS)


def delete_all_data(table):
    try:
        json.loads(
            APIResponse.model_dump_json(Supabase.client.table(table).delete().gte('id', 0).execute()))
        Logger.logger.info(f"Table: {table} || deleted all data")
    except Exception as e:
        Logger.logger.error(f"Table: {table} || delete_all_data failed: {e}")

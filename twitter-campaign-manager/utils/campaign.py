from datetime import datetime

from dateutil.parser import parse

from database.queries.get_queries import get_current_campaign, get_campaign_times
from database.queries.update_queries import update_campaign_status
from utils.misc import is_postgres_exception
from utils.logger import Logger


def get_active_campaign(_exit=True):
    campaign = get_current_campaign()
    if len(campaign) > 0:
        return campaign[0]
    else:
        Logger.logger.error('No active campaign')
        if _exit:
            exit(1)
        else:
            return None


def activate_next_campaign():
    data = get_campaign_times()
    current_time = datetime.timestamp(datetime.utcnow())
    for campaign in data:
        if parse(campaign['start_time']).timestamp() < current_time < parse(campaign['end_time']).timestamp():
            response = update_campaign_status(campaign['id'], True)

            if is_postgres_exception(response):
                Logger.logger.error(f"Failed to activate campaign {campaign['id']}")
                exit(1)

            Logger.logger.info(f"Activated campaign {campaign['id']}")
            return
    Logger.logger.warning('Did not activate a campaign')
    exit(1)


def is_campaign_over(end_time):
    return datetime.timestamp(datetime.utcnow()) > parse(end_time).timestamp()

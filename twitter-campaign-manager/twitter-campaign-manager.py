from bin.collect_posts import collect_new_posts
from bin.update_data import update_data, DataType
from database.queries.get_queries import get_winners, get_prizes
from database.queries.update_queries import set_total_score, update_campaign_status, archive_posts, archive_users
from telegram.api import post_to_channel
from telegram.posts import campaign_end
from utils.campaign import get_active_campaign, is_campaign_over, activate_next_campaign
from utils.raffle import calculate_raffle_winner

if __name__ == '__main__':
    campaign = get_active_campaign(_exit=False)
    if campaign is None:
        activate_next_campaign()
        campaign = get_active_campaign(_exit=False)

    collect_new_posts()
    update_data(DataType.POST)
    update_data(DataType.USER)

    campaign_finished = is_campaign_over(campaign['end_time'])
    if campaign_finished:
        calculate_raffle_winner(campaign)
        set_total_score(campaign['id'])
        update_campaign_status(campaign['id'], False)

        archive_posts(campaign['id'])
        archive_users(campaign['id'])

        winners = get_winners(campaign['id'])
        prizes = get_prizes(campaign['id'])
        post_to_channel(campaign_end(campaign['id'], winners, prizes))

        activate_next_campaign()

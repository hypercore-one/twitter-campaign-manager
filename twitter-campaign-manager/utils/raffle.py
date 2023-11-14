from random import Random

from database.queries.get_queries import get_raffle_data
from database.queries.update_queries import set_raffle_seed, set_raffle_winner


def calculate_raffle_winner(campaign):
    raffle_data = get_raffle_data(campaign)
    if len(raffle_data) == 0:
        return 0

    score_total = 0
    for user in raffle_data:
        score_total += user['score']

    raffle_seed = Random().randint(0, score_total)
    set_raffle_seed(raffle_seed, campaign['id'])

    tmp_score = 0
    for user in raffle_data:
        tmp_score += user['score']
        if raffle_seed < tmp_score:
            set_raffle_winner(user['id'])
            return

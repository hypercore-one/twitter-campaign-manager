import inflect
from dateutil import parser

from utils.format import format_post_criteria


def campaign_start(campaign):
    return (f'*Campaign {campaign['id']}*\n'
            f'Start time: *{parser.parse(campaign["start_time"])}*\n'
            f'End time: *{parser.parse(campaign["end_time"])}*\n'
            f'Post criteria: {format_post_criteria(campaign["post_criteria"])}\n')


def campaign_end(campaign_id, winners, prizes):
    response = f'*Campaign {campaign_id} Results*\n'

    if len(winners) == 0:
        return response + 'No winners'

    p = inflect.engine()
    for i, w in enumerate(winners):
        if 'raffle_winner' not in w:
            response += f'*{p.ordinal(i + 1)}*: @{w["username"]} (*{w["score"]}*) won *{prizes[str(i + 1)]} ZNN*\n'
        else:
            if len(w['raffle_winner']) > 0:
                w = w['raffle_winner'][0]
                response += f'*Raffle*: @{w["username"]} (*{w["score"]}*) won *{prizes['raffle']} ZNN*\n'
    return response

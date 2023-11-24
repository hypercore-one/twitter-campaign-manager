import os

import yaml


class Config:
    path = ''
    if os.path.split(os.getcwd())[-1] != 'twitter-campaign-manager':
        path = os.path.join('..', path)

    with open(os.path.join(path, 'config.yml'), 'r') as file:
        config_data = yaml.safe_load(file)

    TWITTER_BEARER_TOKEN = config_data['TWITTER_BEARER_TOKEN']
    SUPABASE_URL = config_data['SUPABASE_URL']
    SUPABASE_SERVICE_ROLE_KEY = config_data['SUPABASE_SERVICE_ROLE_KEY']
    SHLINK_API_KEY = config_data['SHLINK_API_KEY']
    TG_BOT_TOKEN = config_data['TG_BOT_TOKEN']
    ANNOUNCEMENT_CHANNEL_ID = config_data['ANNOUNCEMENT_CHANNEL_ID']

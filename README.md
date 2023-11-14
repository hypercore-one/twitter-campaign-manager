# Twitter Campaign Manager

A Python script that collects Twitter posts and user data related to Zenon marketing campaigns.  
All data is stored in a Postgres/Supabase database, including campaign data and post scoring values.
---

### Campaigns

Campaigns are designed to help the community focus their efforts on specific tweeting criteria.  
Each post is given a score based on various Twitter metrics, especially native impressions data.

The top users at the end of a campaign are awarded a prize.  
The other users are entered in a raffle based on their post scores. Higher scores have greater chance of winning.
---

### Setup

```sh
1. git clone https://github.com/hypercore-one/twitter-campaign-manager.git && cd twitter-campaign-manager/twitter-campaign-manager
2. python -m venv venv
3. source venv/bin/activate
4. pip install -r requirements.txt
5. cp example.config.yml config.yml
   - add the keys to the config file
6. python main.py
```
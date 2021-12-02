import os
import re
import requests
import json

from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
from time import sleep



#
# get environment variables
#

load_dotenv()

DISCORD_WEBHOOK_ID = os.getenv('DISCORD_WEBHOOK_ID')
DISCORD_WEBHOOK_HASH = os.getenv('DISCORD_WEBHOOK_HASH')
GUILD_ID = os.getenv('GUILD_ID')
POESESSID = os.getenv('POESESSID')
LEAGUE = os.getenv('LEAGUE')

if DISCORD_WEBHOOK_ID is None or DISCORD_WEBHOOK_HASH is None or GUILD_ID is None or POESESSID is None:
    env_vars = [DISCORD_WEBHOOK_ID, DISCORD_WEBHOOK_HASH, GUILD_ID, POESESSID]
    raise Exception(f'one or more env vars empty: {env_vars}')



#
# constants
#

WEBHOOK_URL = f'https://discord.com/api/webhooks/{DISCORD_WEBHOOK_ID}/{DISCORD_WEBHOOK_HASH}'
POE_GUILD_URL = f'https://www.pathofexile.com/guild/profile/{GUILD_ID}'
POE_LADDER_URL = 'https://www.pathofexile.com/api/ladders'

HTTP_HEADERS = { 'User-Agent': 'tojurnru:poe-guild-ranking' }
COOKIES = dict(POESESSID=POESESSID)



#
# functions
#

def request_auto_retry(url):
    retry_count = 0
    while True:
        try:
            response = requests.get(url, headers = HTTP_HEADERS, cookies=COOKIES)
            status_code = response.status_code

            if status_code >= 500:
                raise ValueError(f'HTTP ERROR {status_code}, URL: {url}')

            print(f'        HTTP Response: {status_code}, URL: {url}')
            sleep(5)
            return response

        except Exception as error:
            if retry_count >= 3:
                raise error

            retry_count += 1
            print(error)
            print(f'        HTTP Request Error, retry in 5 minutes...')
            sleep(5*60)



def get_guild_member_list():
    response = request_auto_retry(POE_GUILD_URL)
    status_code = response.status_code

    if status_code != 200:
        raise Exception(f'HTTP Response {status_code}: {response.reason} (URL {url})')

    soup = BeautifulSoup(response.content, 'html.parser')
    divMembers = soup.select('.details-content .member')

    members = []
    for idx, member in enumerate(divMembers):
        a = member.select('a')[0]
        name = a.contents[0]
        members.append(name.lower())

    return members



def is_in_array(query, array):
    for data in array:
        if query == data:
            return True
    return False



def get_rankings(member_list):
    member_entries = []

    max_entries = 15000 # 15000
    limit = 200 # 200
    offset = 0

    while offset < max_entries:

        # query data from pathofexile.com
        url = f'{POE_LADDER_URL}/{LEAGUE}?sort=depth&limit={limit}&offset={offset}'
        response = request_auto_retry(url)
        status_code = response.status_code

        if status_code != 200:
            raise Exception(f'HTTP Response {status_code}: {response.reason} (URL {url})')

        entries = response.json()['entries']

        # obtain members only entries
        for entry in entries:
            entry_name = entry['account']['name'].lower()
            if is_in_array(entry_name, member_list):
                member_entries.append(entry)

        # process loop
        offset += limit

    return member_entries        



def generate_and_post_to_discord(member_entries):

    col_account = []
    col_character = []
    col_depth = []

    for entry in member_entries:
        account_name = entry['account']['name']
        character_name = entry['character']['name']
        character_class = entry['character']['class']
        depth = entry['character']['depth']['default']

        col_account.append(account_name)
        col_character.append(f'{character_name} ({character_class})')
        col_depth.append(str(depth)) # convert to string

    embed = DiscordEmbed(
        title='Guild Rankings',
        description=f'Delve Rankings in {LEAGUE}',
        color='00ff00'
    )

    embed.add_embed_field(name='Account', value='\n'.join(col_account), inline=True)
    embed.add_embed_field(name='Character', value='\n'.join(col_character), inline=True)
    embed.add_embed_field(name='Depth', value='\n'.join(col_depth), inline=True)

    embed.set_footer(text=''.join([char*100 for char in '_']))

    webhook = DiscordWebhook(url=WEBHOOK_URL)
    webhook.add_embed(embed)
    webhook.execute()
    sleep(1)



#
# start
#

member_list = get_guild_member_list()
print(member_list)

member_entries = get_rankings(member_list)
print(member_entries)

generate_and_post_to_discord(member_entries)

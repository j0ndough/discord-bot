import datetime as dt
import httpx

from datetime import datetime
from dotenv import dotenv_values

# Get API key
config = dotenv_values('.env')
auth = '?api_key=' + config.get('LEAGUE_API_KEY')

RIOT_URL = 'https://americas.api.riotgames.com'
LOL_URL = 'https://na1.api.riotgames.com'


# Returns a dict containing the current ingame status for a user.
# This function uses multiple get functions to get and process spectator information.
async def request_status(name: str, tag: str) -> dict:
    puuid = await get_puuid(name, tag)
    if not puuid:
        return {'status':'Invalid Riot ID.', 'gameTime':'N/A'}
    esid = await get_esid(puuid)
    if not esid:
        return {'status':'Valid Riot ID but no League account.', 'gameTime':'N/A'}
    status = await get_ingame_status(esid)
    if not status:
        return {'status':'User is not in-game.', 'gameTime':'N/A'}
    else:
        return {'status':f'In-Game ({status["mode"]})', 'gameTime':status['time']}


# Returns a player's encrypted summoner ID from their puuid as a string.
# If the puuid is invalid, returns an empty string.
async def get_esid(puuid: str) -> str:
    endpoint = '/lol/summoner/v4/summoners/by-puuid/'
    json = await make_request(LOL_URL, endpoint, puuid)
    if not json:
        return ''
    else:
        return json['id']


# Returns a player's puuid from their Riot ID as a string.
# If the Riot ID is invalid, returns an empty string.
async def get_puuid(name: str, tag: str) -> str:
    endpoint = '/riot/account/v1/accounts/by-riot-id/'
    query = name + '/' + tag
    json = await make_request(RIOT_URL, endpoint, query)
    if not json:
        return ''
    else:
        return json['puuid']


# Retrieves live info about a player's ingame status from spectator info.
# If the player is not ingame, returns an empty dict.
async def get_ingame_status(esid: str) -> dict:
    endpoint = '/lol/spectator/v4/active-games/by-summoner/'
    json = await make_request(LOL_URL, endpoint, esid)
    if not json:
        return {}
    else:
        cur_mode = json['gameMode']
        if json['gameStartTime'] == 0:
            cur_time = '0:00'
        else:
            delta = datetime.now() - datetime.fromtimestamp(json['gameStartTime'] / 1000)
            mins = delta.seconds // 60
            secs = delta.seconds % 60
            cur_time = str(mins).zfill(2) + ':' + str(secs).zfill(2)  # zero pad mins/secs
        status = {
            'mode': cur_mode,
            'time': cur_time
        }
        return status


# Makes a HTTP request at the given endpoint.
# If successful, returns a dict containing the json response, or an empty dict is the response is a 404.
# Otherwise, prints error to console and exits the program.
async def make_request(url: str, endpoint: str, query: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url + endpoint + query + auth)
            response.raise_for_status()
            json_response = response.json()
            return json_response
    except httpx.HTTPError as http_err:
        # When id or match is not found
        if response.status_code == 404:
            return {}

        # Otherwise, print error and exit program
        print(http_err)
        raise SystemError
    except Exception as e:
        print('Other error occurred. ' + e)
        raise SystemError
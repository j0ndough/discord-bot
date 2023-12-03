import configparser
import httpx

# get API key
config = configparser.ConfigParser()
config.read('api_config.cfg')
auth = '?api_key=' + config['Credentials']['LEAGUE_API_KEY']

RIOT_URL = 'https://americas.api.riotgames.com'
LOL_URL = 'https://na1.api.riotgames.com'


async def get_encrypted_summ_id(puuid: str) -> str:
    endpoint = '/lol/summoner/v4/summoners/by-puuid/'
    json = await make_request(LOL_URL, endpoint, puuid)
    if not json:
        return ''
    else:
        return json['id']


async def get_puuid(name: str, tag: str) -> str:
    endpoint = '/riot/account/v1/accounts/by-riot-id/'
    query = name + '/' + tag
    json = await make_request(RIOT_URL, endpoint, query)
    if not json:
        return ''
    else:
        return json['puuid']


async def get_ingame_status(eid: str):
    endpoint = '/lol/spectator/v4/active-games/by-summoner/'
    json = await make_request(LOL_URL + endpoint + eid)
    if not json:
        return ''
    else:
        return json


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
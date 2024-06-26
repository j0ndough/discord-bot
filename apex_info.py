import asyncio
import httpx

from dotenv import dotenv_values

# Get API key from config
config = dotenv_values('.env')
auth = '?auth=' + config.get('APEX_API_KEY')
BASE_URL = 'https://api.mozambiquehe.re/'
CRAFTING_ENDPOINT = 'crafting'
MAP_ENDPOINT = 'maprotation'
STATUS_ENDPOINT = 'servers'

# Define rarities
rarities = {
    'Common': '⬜',
    'Rare': '🟦',
    'Epic': '🟪',
    'Legendary': '🟨'
}


# Returns a dict of the current crafting rotation.
async def get_crafting() -> dict:
    params = {}
    json = await make_request(CRAFTING_ENDPOINT, params)
    items = get_current_crafting(json)
    return items


# Returns a dict of the current map rotation.
async def get_maps() -> dict:
    params = {'version': '2'}
    json = await make_request(MAP_ENDPOINT, params)
    maps = get_current_maps(json)
    return maps


# Returns a dict of the current matchmaking server status.
async def get_status() -> dict:
    params = {}
    json = await make_request(STATUS_ENDPOINT, params)
    status = get_current_status(json)
    return status


# Makes a HTTP request at the given endpoint.
# Returns a dict containing the json response, or prints an error if it fails and exits the program.
async def make_request(req: str, params: dict) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL + req + auth, params=params)
            response.raise_for_status()
            json_response = response.json()
            return json_response
    except httpx.HTTPError as http_err:
        print(http_err)
        raise SystemError
    except Exception as e:
        print('Other error occurred. ' + e)
        raise SystemError


# Deprecated due to crafting update ingame.
# Returns a dict of parsed json data about the current crafting rotation.
def get_current_crafting(json: dict) -> dict:
    items = {}
    for j in json:
        for b in j['bundleContent']:
            item = capitalize_string(b['itemType']['name'].replace('_', ' '))
            rarity = b['itemType']['rarity']
            rarity = rarities[rarity] + ' ' + rarity
            cost = b['cost']
            if item not in items:
                items[item] = 'Rarity: ' + rarity + ' | Cost: ' + str(cost)
    return items


# Returns a dict of parsed json data about the current map rotation.
def get_current_maps(json: dict) -> dict:
    res = {}
    res['BR Pubs'] = json['battle_royale']['current']['map']
    res['BR Ranked'] = json['ranked']['current']['map']
    res['LTM - ' + json['ltm']['current']['eventName']] = json['ltm']['current']['map']
    return res


# # Returns a dict of parsed json data about the current matchmaking server status.
def get_current_status(json: dict) -> dict:
    servers = json['EA_novafusion']
    res = dict.fromkeys(['EU West', 'EU East', 'US West', 'US Central', 'US East', 'South America', 'Asia'])
    for s, r in zip(servers, res):
        res[r] = 'Status: ' + servers[s]['Status'] + ', Response Time: ' + str(servers[s]['ResponseTime']) + ' ms'
    return res


# Custom function that capitalizes the first letter of every word.
# Compared to other similar functions, this one does not alter the capitalization of other letters.
def capitalize_string(str: str) -> str:
    words = str.split()
    cap_words = [capitalize_first_letter(word) for word in words]
    return ' '.join(cap_words)


# Capitalizes first letter of a word, but leaves the rest untouched.
def capitalize_first_letter(word: str) -> str:
    if word:
        return word[:1].upper() + word[1:]
    else:  # in case input is empty
        return word
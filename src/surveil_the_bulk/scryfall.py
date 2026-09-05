import json
import urllib.parse

import requests
from surveil_the_bulk.models import CardFace, MTGCard

url = "https://api.scryfall.com/cards/named?exact="
headers = {"Accept": "application/json", "User-Agent": "MBO:Magic Bulk Organizer"}


def search_card_exact(card_name, set_code=None):
    search_name = urllib.parse.quote(card_name)
    searchurl = url + search_name
    if set_code != None:
        searchurl += "&set=" + set_code
    
    
    response = requests.get(searchurl, headers=headers)
    response.raise_for_status()

    json_data = response.json()
    return json_data

def normalize_card_data(raw_data: dict):
    card = MTGCard.model_validate(raw_data)
    return card


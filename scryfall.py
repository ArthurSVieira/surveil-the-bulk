import urllib.request
import requests
import urllib.parse
import json

url ='https://api.scryfall.com/cards/named?exact='
headers = {
    "Accept": "application/json",
    "User-Agent": 'MBO:Magic Bulk Organizer'
}



def search_card_exact(card_name):
    search_name = urllib.parse.quote(card_name)  
    searchurl = url + search_name
    response = requests.get(searchurl, headers=headers)
    response.raise_for_status()

    json_data = response.json()
    return json_data
    

print(search_card_exact('Sol Ring').name)
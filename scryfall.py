import requests
import urllib.parse
import sqlite3
import json

url ='https://api.scryfall.com/cards/named?exact='
headers = {
    "Accept": "application/json",
    "User-Agent": 'MBO:Magic Bulk Organizer'
}
col = sqlite3.connect('collection.db')


def search_card_exact(card_name, set_code=None):
    search_name = urllib.parse.quote(card_name)  
    searchurl = url + search_name 
    if(set_code != None):
        searchurl+='&set='+set_code
    value = searchurl
    querycheck = ''' SELECT json_data FROM
                scryfall_cache WHERE
                query_url = ?
                '''
    
    cursor = col.execute(querycheck, (searchurl,))
    resultB = cursor.fetchone()
    if(resultB == None):
        response = requests.get(searchurl, headers=headers)
        response.raise_for_status()

        json_data = response.json()
        valuesI = (searchurl, response.text)
        insertquery = ''' INSERT OR IGNORE INTO scryfall_cache (
                    query_url,json_data
                    ) VALUES (?,?)
                    '''
        col.execute(insertquery, valuesI)
        col.commit()
        return json_data
    return  json.loads(resultB[0])
    
def normalize_card_data(raw_card):
     
     if 'card_faces' in raw_card:
            dictcard = {
            'id': raw_card['id'],
            'set_code':raw_card['set'],
            'color_identity':",".join(raw_card['color_identity']),
            'produced_mana':",".join(raw_card.get('produced_mana', [])),
            
            'name':raw_card['card_faces'][0]['name'],
            'mana_cost':raw_card['card_faces'][0]['mana_cost'],
            'type_line':raw_card['card_faces'][0]['type_line'],
            'power':raw_card['card_faces'][0].get('power'),
            'toughness':raw_card['card_faces'][0].get('toughness'),
            'image_url':raw_card['card_faces'][0]['image_uris']['normal'],
            'oracle_text':raw_card['card_faces'][0]['oracle_text'],

            'a_name':raw_card['card_faces'][1]['name'],
            'a_mana_cost':raw_card['card_faces'][1]['mana_cost'],
            'a_type_line':raw_card['card_faces'][1]['type_line'],
            'a_power':raw_card['card_faces'][1].get('power'),
            'a_toughness':raw_card['card_faces'][1].get('toughness'),
            'a_image_url':raw_card['card_faces'][1]['image_uris']['normal'],
            'a_oracle_text':raw_card['card_faces'][1]['oracle_text'],
             }

     else:
        dictcard = {
            'id': raw_card['id'],
            'set_code':raw_card['set'],
            'name':raw_card['name'],
            'mana_cost':raw_card['mana_cost'],
            'type_line':raw_card['type_line'],
            'power':raw_card.get('power'),
            'toughness':raw_card.get('toughness'),
            'image_url':raw_card['image_uris']['normal'],
            'color_identity':",".join(raw_card['color_identity']),
            'produced_mana':",".join(raw_card.get('produced_mana', [])),
            'oracle_text':raw_card['oracle_text'],
             }
     return dictcard

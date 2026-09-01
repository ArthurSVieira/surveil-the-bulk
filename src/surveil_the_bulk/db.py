import sqlite3
import json

from surveil_the_bulk.scryfall import normalize_card_data, search_card_exact

def get_connection():
    conn = sqlite3.connect('collection.db')
    conn.row_factory = sqlite3.Row
    return conn


def insert_card(card_data):
    conn = get_connection()
    collumns = [
        "id",
        "name",
        "produced_mana",
        "color_identity",
        "power",
        "toughness",
        "mana_cost",
        "type_line",
        "set_code",
        "oracle_text",
        "image_url",
        "a_name",
        "a_mana_cost",
        "a_type_line",
        "a_power",
        "a_toughness",
        "a_image_url",
        "a_oracle_text",
    ]

    sql = """
    INSERT OR IGNORE INTO cards (
        id, name, produced_mana, color_identity, power, toughness, mana_cost, 
        type_line, set_code, oracle_text, image_url,
        a_name, a_mana_cost, a_type_line, a_power, a_toughness, a_image_url, a_oracle_text
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = tuple(card_data.get(col) for col in collumns)
    conn.execute(sql, values)
    conn.commit()
    conn.close()
    print(f" {card_data.get('name')} added to database ")


def init_db():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute(""" CREATE TABLE IF NOT EXISTS tags(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(50) NOT NULL DEFAULT '#3b82f6',
    description TEXT
    )
    """)

    conn.execute(""" CREATE TABLE IF NOT EXISTS decks(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL,
    format VARCHAR(50),
    color_ident VARCHAR(50) NOT NULL
    )
    """)

    conn.execute(""" CREATE TABLE IF NOT EXISTS cards(
    id TEXT PRIMARY KEY NOT NULL,
    own_qty INT DEFAULT 0,
    wnt_qty INT DEFAULT 0,
    trd_qty INT DEFAULT 0,
    name VARCHAR(50) NOT NULL,
    produced_mana TEXT,
    color_identity TEXT,
    power VARCHAR(50),
    toughness VARCHAR(50),
    mana_cost VARCHAR(50),
    type_line VARCHAR(50), 
    set_code  VARCHAR(50),
    oracle_text TEXT,
    image_url TEXT,

    a_name VARCHAR(50),
    a_mana_cost VARCHAR(50),
    a_type_line VARCHAR(50),
    a_power VARCHAR(50),
    a_toughness VARCHAR(50),
    a_image_url TEXT,
    a_oracle_text TEXT
    )
    """)

    conn.execute(""" CREATE TABLE IF NOT EXISTS card_tags(
    card_id TEXT NOT NULL ,
    tag_id INT NOT NULL,
    PRIMARY KEY (card_id, tag_id),
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
    )
    """)

    conn.execute(""" CREATE TABLE IF NOT EXISTS card_decks(
    card_id TEXT NOT NULL ,
    deck_id INT NOT NULL ,
    quantity INT NOT NULL DEFAULT 1,
    board_type TEXT NOT NULL DEFAULT 'Mainboard',
    PRIMARY KEY (card_id, deck_id, board_type),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
    )
    """)

    conn.execute(""" CREATE TABLE IF NOT EXISTS scryfall_cache(
    card_name TEXT NOT NULL,
    set_code TEXT,
    json_data TEXT NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (card_name, set_code)
    )
    """)

    conn.commit()
    conn.close()


def get_cached_response(card_name, set_code=None):
    conn = get_connection()
    query = """ SELECT json_data FROM scryfall_cache WHERE
            card_name = ? and set_code is ? 
    """
    cursor = conn.execute(query, (card_name, set_code))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result['json_data'])
    return None


def save_cached_response(card_name, set_code, raw_json_data):
    conn = get_connection()
    insertquery = """
    INSERT OR IGNORE INTO scryfall_cache (card_name, set_code, json_data) 
    VALUES (?, ?, ?)
    """

    json_string = json.dumps(raw_json_data) 
    
    conn.execute(insertquery, (card_name, set_code, json_string))
    conn.commit()
    conn.close()


def add_card_to_deck(deck_name, card_name, quantity):
    conn = get_connection()
    cQuery = """ SELECT id from cards WHERE name = ? """
    cursor = conn.execute(cQuery, (card_name,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        update_inventory(card_name, 0, 1, 0)
        conn = get_connection()
        cursor = conn.execute(cQuery, (card_name,))
        result = cursor.fetchone()
        conn.close()
        
    cardId = result['id']

    conn = get_connection()
    dQuery = """ SELECT id from decks WHERE name = ? """
    cursor = conn.execute(dQuery, (deck_name,))
    result = cursor.fetchone()
    deckId = result['id']

    sql = """INSERT OR IGNORE INTO card_decks 
            (card_id, deck_id, quantity) VALUES (?,?,?)
    """
    values = (cardId, deckId, quantity)
    conn.execute(sql, values)
    conn.commit()
    conn.close()
    print("Cartas adicionadas ao deck!")


def show_decklist(deck_name):
    conn = get_connection()
    query = """ SELECT c.name, cd.quantity, cd.board_type FROM 
card_decks cd JOIN decks d on cd.deck_id = d.id
JOIN cards c on c.id = cd.card_id WHERE d.name = ?"""

    cursor = conn.execute(query, (deck_name,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        card = {
            "name": row['name'],
            "quantity": row['quantity'],
            "board_type": row['board_type'],
        }
        result.append(card)
    return result


def add_card(card, setC=None):
    rawdata = get_cached_response(card, setC)
    if rawdata is None:
        rawdata = search_card_exact(card, setC)
        save_cached_response(card, setC, rawdata)
    insert_card(normalize_card_data(rawdata))


def add_deck(name, format, color_identity):
    conn = get_connection()
    query = """ INSERT OR IGNORE INTO decks(
        name, format, color_ident) VALUES (?,?,?)        
    """
    values = (name, format, color_identity)
    conn.execute(query, values)
    conn.commit()
    conn.close()
    print(f"new deck: {name} added to database")


def update_inventory(card, own_qty=0, wnt_qty=0, trd_qty=0):
    add_card(card)
    conn = get_connection()
    sql = """
    UPDATE cards 
    SET own_qty = own_qty + ?, 
        wnt_qty = wnt_qty + ?, 
        trd_qty = trd_qty + ?
    WHERE name = ?
    """
    values = (own_qty, wnt_qty, trd_qty, card)
    conn.execute(sql, values)
    conn.commit()
    conn.close()
    print(f"Inventario de {card} atualizado! ")


def view_colection(filter_type="all"):
    conn = get_connection()
    if filter_type == "bulk":
        query = "SELECT name, own_qty, wnt_qty, trd_qty FROM cards WHERE own_qty > 0"
    elif filter_type == "trade":
        query = "SELECT name, own_qty, wnt_qty, trd_qty FROM cards WHERE trd_qty > 0"
    elif filter_type == "want":
        query = "SELECT name, own_qty, wnt_qty, trd_qty FROM cards WHERE wnt_qty > 0"
    elif filter_type == "all":
        query = "SELECT name, own_qty, wnt_qty, trd_qty FROM cards WHERE wnt_qty > 0 OR trd_qty > 0 OR own_qty > 0"
    else:
        print("Filtro inválido! Escolha 'bulk', 'trade', 'want' ou 'all'.")
        conn.close()
        return

    cursor = conn.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        carta = {
            "name": row['name'],
            "own_qty": row['own_qty'],
            "wnt_qty": row['wnt_qty'],
            "trd_qty": row['trd_qty'],
        }
        result.append(carta)

    return result


def view_decks():
    conn = get_connection()
    query = "SELECT name, format, color_ident FROM decks"
    cursor = conn.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        deck = {"name": row['name'], "format": row['format'], "color_ident": row['color_ident']}
        result.append(deck)
    return result
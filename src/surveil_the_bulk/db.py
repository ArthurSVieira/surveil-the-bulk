import sqlite3
import json

from surveil_the_bulk.models import CardFace, MTGCard
from surveil_the_bulk.scryfall import normalize_card_data, search_card_exact

def get_connection():
    conn = sqlite3.connect('collection.db')
    conn.row_factory = sqlite3.Row
    return conn


def insert_card(card: MTGCard):
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")

    Cquery = """ INSERT OR IGNORE INTO cards (
        id,set_code, collector_number,cmc,price_usd,price_usd_foil,
        color_identity,produced_mana,legalities) VALUES (
        ?,?,?,?,?,?,?,?,?)
    """
    Cvalues = (
        card.id,
        card.set_code,
        card.collector_number,
        card.cmc,
        100 * card.price_usd if card.price_usd else 0,
        100 * card.price_usd_foil if card.price_usd_foil else 0,
        "".join(card.color_identity),
        "".join(card.produced_mana) if card.produced_mana else 0,
        ",".join(card.legalities)
    )
    conn.execute(Cquery,Cvalues)
    for index, face in enumerate(card.card_faces):
        conn.execute (""" INSERT OR IGNORE INTO card_faces (
        card_id,face_index,name,power,toughness,
        mana_cost,type_line,oracle_text,image_url) VALUES 
        (?,?,?,?,?,?,?,?,?)
        """,(
            card.id,
            index,
            face.name,
            face.power,
            face.toughness,
            face.mana_cost,
            face.type_line,
            face.oracle_text,
            face.image_url
        )
        )
    conn.commit()
    conn.close()
    print(f" {card.card_faces[0].name} added to database ")


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
        set_code TEXT,
        collector_number TEXT,
        cmc REAL,
        price_usd REAL,
        price_usd_foil REAL,
        color_identity TEXT,
        produced_mana TEXT,
        legalities TEXT,
        own_qty INT DEFAULT 0,
        wnt_qty INT DEFAULT 0,
        trd_qty INT DEFAULT 0
    )"""
    )

    conn.execute(""" CREATE TABLE IF NOT EXISTS card_faces(
        card_id TEXT NOT NULL,
        face_index INT NOT NULL,
        name TEXT NOT NULL,
        mana_cost TEXT,
        type_line TEXT,
        oracle_text TEXT,
        image_url TEXT,
        power TEXT,
        toughness TEXT,
        PRIMARY KEY (card_id, face_index),
        FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
    )""")

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
    cQuery = """ SELECT c.id FROM cards c 
        JOIN card_faces cf ON c.id = cf.card_id 
        WHERE cf.name = ? AND cf.face_index = 0"""
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
    query = """ SELECT cf.name, cd.quantity, cd.board_type FROM 
    card_decks cd JOIN decks d on cd.deck_id = d.id
    JOIN cards c on c.id = cd.card_id 
    JOIN card_faces cf on c.id = cf.card_id 
    WHERE d.name = ? AND cf.face_index = 0   
    """

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
    WHERE id = (SELECT card_id FROM card_faces 
    WHERE name = ? AND face_index = 0)
    """
    values = (own_qty, wnt_qty, trd_qty, card)
    conn.execute(sql, values)
    conn.commit()
    conn.close()
    print(f"Inventario de {card} atualizado! ")


def view_colection(filter_type="all"):
    conn = get_connection()
    if filter_type == "bulk":
        query = """SELECT cf.name, c.own_qty, c.wnt_qty, c.trd_qty 
                FROM cards c 
                JOIN card_faces cf ON c.id = cf.card_id 
                WHERE cf.face_index = 0 AND c.own_qty > 0"""
    elif filter_type == "trade":
        query = """SELECT cf.name, c.own_qty, c.wnt_qty, c.trd_qty 
                FROM cards c 
                JOIN card_faces cf ON c.id = cf.card_id 
                WHERE cf.face_index = 0 AND c.trd_qty > 0"""
    elif filter_type == "want":
        query = """SELECT cf.name, c.own_qty, c.wnt_qty, c.trd_qty 
                FROM cards c 
                JOIN card_faces cf ON c.id = cf.card_id 
                WHERE cf.face_index = 0 AND c.wnt_qty > 0"""
    elif filter_type == "all":
        query = """SELECT cf.name, c.own_qty, c.wnt_qty, c.trd_qty 
                FROM cards c 
                JOIN card_faces cf ON c.id = cf.card_id 
                WHERE cf.face_index = 0 AND (c.own_qty > 0 OR c.wnt_qty > 0 OR c.trd_qty > 0)"""
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
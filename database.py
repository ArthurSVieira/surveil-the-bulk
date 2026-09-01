import sqlite3

from scryfall import normalize_card_data, search_card_exact

col = sqlite3.connect("collection.db")


def insert_card(card_data):
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
    col.execute(sql, values)
    col.commit()
    print(f" {card_data.get('name')} added to database ")


def init_db():
    col.execute("PRAGMA foreign_keys = ON")

    col.execute(""" CREATE TABLE IF NOT EXISTS tags(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(50) NOT NULL DEFAULT '#3b82f6',
    description TEXT
    )
    """)

    col.execute(""" CREATE TABLE IF NOT EXISTS decks(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL,
    format VARCHAR(50),
    color_ident VARCHAR(50) NOT NULL
    )
    """)

    col.execute(""" CREATE TABLE IF NOT EXISTS cards(
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

    col.execute(""" CREATE TABLE IF NOT EXISTS card_tags(
    card_id TEXT NOT NULL ,
    tag_id INT NOT NULL,
    PRIMARY KEY (card_id, tag_id),
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE

    )
    """)

    col.execute(""" CREATE TABLE IF NOT EXISTS card_decks(
    card_id TEXT NOT NULL ,
    deck_id INT NOT NULL ,
    quantity INT NOT NULL DEFAULT 1,
    board_type TEXT NOT NULL DEFAULT 'Mainboard',
    PRIMARY KEY (card_id, deck_id, board_type),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE

    )
    """)

    col.execute(""" CREATE TABLE IF NOT EXISTS scryfall_cache(
    query_url TEXT PRIMARY KEY NOT NULL,
    json_data TEXT NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
    )
    """)

    col.commit()


init_db()


def add_card_to_deck(deck_name, card_name, quantity):
    cQuery = """ SELECT id from cards WHERE
                name = ?
    """
    cursor = col.execute(cQuery, (card_name,))
    result = cursor.fetchone()
    if result == None:
        update_inventory(card_name, 0, 1, 0)
        cursor = col.execute(cQuery, (card_name,))
        result = cursor.fetchone()
    cardId = result[0]

    dQuery = """ SELECT id from decks WHERE
                name = ?
    """
    cursor = col.execute(dQuery, (deck_name,))
    result = cursor.fetchone()
    deckId = result[0]

    sql = """INSERT OR IGNORE INTO card_decks 
            (card_id, deck_id, quantity) VALUES (?,?,?)

    """
    values = (cardId, deckId, quantity)
    col.execute(sql, values)
    col.commit()
    print("Cartas adicionadas ao deck!")


def show_decklist(deck_name):
    query = """ SELECT c.name, cd.quantity, cd.board_type FROM 
card_decks cd JOIN decks d on cd.deck_id = d.id
JOIN cards c on c.id = cd.card_id WHERE d.name = ?"""

    cursor = col.execute(query, (deck_name,))
    rows = cursor.fetchall()

    result = []
    for row in rows:
        card = {
            "name": row[0],
            "quantity": row[1],
            "board_type": row[2],
        }
        result.append(card)
    return result


def add_card(card, setC=None):

    rawdata = search_card_exact(card, setC)
    insert_card(normalize_card_data(rawdata))


def add_deck(name, format, color_identity):
    query = """ INSERT OR IGNORE INTO decks(
        name, format, color_ident) VALUES (?,?,?)        
    """
    values = (name, format, color_identity)
    col.execute(query, values)
    col.commit()
    print(f"new deck: {name} added to database")


def update_inventory(card, own_qty=0, wnt_qty=0, trd_qty=0):
    add_card(card)
    sql = """
    UPDATE cards 
    SET own_qty = own_qty + ?, 
        wnt_qty = wnt_qty + ?, 
        trd_qty = trd_qty + ?
    WHERE name = ?
    """
    values = (own_qty, wnt_qty, trd_qty, card)
    col.execute(sql, values)
    col.commit()
    print(f"Inventario de {card} atualizado! ")


def view_colection(filter_type="all"):
    if filter_type == "bulk":
        query = """
        SELECT name,own_qty, wnt_qty , trd_qty FROM
        cards WHERE
        own_qty > 0
        """
    elif filter_type == "trade":
        query = """
        SELECT name,own_qty, wnt_qty , trd_qty FROM
        cards WHERE
        trd_qty > 0
        """
    elif filter_type == "want":
        query = """
        SELECT name,own_qty, wnt_qty , trd_qty FROM
        cards WHERE
        wnt_qty > 0
        """
    elif filter_type == "all":
        query = """
        SELECT name,own_qty, wnt_qty , trd_qty FROM
        cards WHERE
        wnt_qty > 0 OR trd_qty > 0 OR own_qty >0
        """
    else:
        print("Filtro inválido! Escolha 'bulk', 'trade', 'want' ou 'all'.")
        return

    cursor = col.execute(query)
    rows = cursor.fetchall()
    result = []
    for row in rows:
        carta = {
            "name": row[0],
            "own_qty": row[1],
            "wnt_qty": row[2],
            "trd_qty": row[3],
        }
        result.append(carta)

    return result


def view_decks():
    query = """SELECT name, format, color_ident FROM
    decks """
    cursor = col.execute(query)
    rows = cursor.fetchall()
    result = []
    for row in rows:
        deck = {"name": row[0], "format": row[1], "color_ident": row[2]}
        result.append(deck)
    return result

import sqlite3

col = sqlite3.connect('collection.db')



def init_db():
    col.execute('PRAGMA foreign_keys = ON')

    col.execute(''' CREATE TABLE IF NOT EXISTS tags(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(50) NOT NULL DEFAULT '#3b82f6',
    description TEXT
    )
    ''')

    col.execute(''' CREATE TABLE IF NOT EXISTS decks(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL,
    format VARCHAR(50),
    color_ident VARCHAR(50) NOT NULL
    )
    ''')

    col.execute(''' CREATE TABLE IF NOT EXISTS cards(
    id TEXT PRIMARY KEY NOT NULL,
    name VARCHAR(50) NOT NULL,
    mana_cost VARCHAR(50),
    type_line VARCHAR(50), 
    set_code  VARCHAR(50),
    image_url TEXT
    )
    ''')

    col.execute(''' CREATE TABLE IF NOT EXISTS card_tags(
    card_id TEXT NOT NULL ,
    tag_id INT NOT NULL,
    PRIMARY KEY (card_id, tag_id),
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE

    )
    ''')
    
    col.execute(''' CREATE TABLE IF NOT EXISTS card_decks(
    card_id TEXT NOT NULL ,
    deck_id INT NOT NULL ,
    quantity INT NOT NULL DEFAULT 1,
    board_type TEXT NOT NULL DEFAULT 'Mainboard',
    PRIMARY KEY (card_id, deck_id, board_type),
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE

    )
    ''')

    col.execute(''' CREATE TABLE IF NOT EXISTS scryfall_cache(
    query_url TEXT PRIMARY KEY NOT NULL,
    json_data TEXT NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
    )
    ''')
    

    col.commit()
    return

init_db()
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

    col.commit()
    return

init_db
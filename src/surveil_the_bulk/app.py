from aiohttp import web
from surveil_the_bulk.routes import (
    update_collection,
    create_deck,
    get_decks,
    get_collection,
    insert_card_to_deck,
    get_decklist,
    status
)
from surveil_the_bulk.db import init_db

def main():
    init_db()
    app = web.Application()
    app.add_routes(
        [
            web.get("/api/status", status),
            web.get("/api/decks", get_decks),
            web.get("/api/cards", get_collection),
            web.get("/api/decks/cards", get_decklist),
            web.post("/api/decks", create_deck),
            web.post("/api/decks/cards", insert_card_to_deck),
            web.post("/api/cards", update_collection),
        ]
    )

    web.run_app(app)

from aiohttp import web

from surveil_the_bulk.db import (
    add_card_to_deck,
    add_deck,
    show_decklist,
    update_inventory,
    view_colection,
    view_decks,
)


async def update_collection(request):
    dados = await request.json()

    card = dados.get("name")
    own_qty = dados.get("own_qty", 0)
    wnt_qty = dados.get("wnt_qty", 0)
    trd_qty = dados.get("trd_qty", 0)

    update_inventory(card, own_qty, wnt_qty, trd_qty)
    return web.Response(text="Colecao atualizada com sucesso")


async def create_deck(request):
    dados = await request.json()

    name = dados.get("name")
    format = dados.get("format")
    color = dados.get("color_ident")

    add_deck(name, format, color)
    return web.Response(text="Deck adicionado com sucesso")


async def get_decks(request):
    return web.json_response(view_decks())


async def get_collection(request):
    filtr = request.query.get("filter", "all")
    return web.json_response(view_colection(filtr))


async def insert_card_to_deck(request):
    dados = await request.json()
    deck_name = dados.get("deck_name")
    card_name = dados.get("card_name")
    quantity = dados.get("quantity")

    add_card_to_deck(deck_name, card_name, quantity)
    return web.Response(text="Carta adicionada ao deck")


async def get_decklist(request):
    deck_name = request.query.get("deck")
    return web.json_response(show_decklist(deck_name))


async def status(request):
    server_data = {"status": "StB API online", "version": "1.0"}

    return web.json_response(server_data)



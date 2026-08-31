from aiohttp import web
from database import view_colection, update_inventory, view_decks, add_deck
import json 

async def update_collection(request):
    dados = await request.json()

    card = dados.get('name')
    own_qty = dados.get('own_qty', 0)
    wnt_qty = dados.get('wnt_qty', 0)
    trd_qty = dados.get('trd_qty', 0)

    update_inventory(card,own_qty,wnt_qty,trd_qty)
    return web.Response(text="Colecao atualizada com sucesso")

async def create_deck(request):
    dados = await request.json()

    name = dados.get('name')
    format = dados.get('format')
    color =  dados.get('color_ident')

    add_deck(name, format, color)
    return web.Response(text="Deck adicionado com sucesso")
    

async def get_decks(request):
    return web.json_response(view_decks())

async def get_collection(request):
    filtr = request.query.get('filter', 'all')
    return web.json_response(view_colection(filtr))

async def status(request):
    server_data = {
        'status': "StB API online",
        'version': '1.0'
    }

    return web.json_response(server_data)

app = web.Application()
app.add_routes([web.get('/api/status', status),
                web.get('/api/decks', get_decks),
                web.get('/api/cards', get_collection),
                web.post('/api/decks', create_deck),
                web.post('/api/cards', update_collection)])

web.run_app(app)

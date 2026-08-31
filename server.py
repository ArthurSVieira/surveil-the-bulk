from aiohttp import web
from database import view_colection
import json 

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
                web.get('/api/cards', get_collection)])

web.run_app(app)

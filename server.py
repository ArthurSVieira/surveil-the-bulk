from aiohttp import web
import json 

async def status(request):
    server_data = {
        'status': "StB API online",
        'version': '1.0'
    }

    return web.json_response(server_data)

app = web.Application()
app.add_routes([web.get('/api/status', status)])

web.run_app(app)

from .views.index import IndexView
from .app import Datasette
import json


datasette = Datasette(
    ['fixtures.db'],
    cache_headers=True,
    cors=True,
)
datasette.inspect()
datasette.app()


class App():
    def __init__(self, scope):
        self.scope = scope

    async def __call__(self, receive, send):

        view = IndexView(datasette)
        blah = await view.get(None, '.json')

        print('blah', blah)

        print('path', self.scope['path'])
        print('query_string', self.scope['query_string'].decode('utf8'))
        print()
        print('scope', self.scope)
        print((await receive()))

        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/html'],
            ]
        })
        await send({
            'type': 'http.response.body',
            'body': blah.body,
        })

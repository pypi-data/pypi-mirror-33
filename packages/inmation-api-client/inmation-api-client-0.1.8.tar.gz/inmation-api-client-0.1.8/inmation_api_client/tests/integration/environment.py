from options import Options
from inclient import Client

WS_URL = 'ws://127.0.0.1:8000/ws'
OPTIONS = Options('so', 'inmation')
OPTIONS.tim = 10
ITEMS_PATH = '/System/Core/TestWebSocket/'

ITEM1 = ITEMS_PATH + 'Item01' # Generic Item
ITEM2 = ITEMS_PATH + 'Item02' # Generic Item
ITEM3 = ITEMS_PATH + 'Item03' # Generic Item

def create_api_client(ioloop):
    client = Client(ioloop)

    ioloop.run_until_complete(client.connect_ws(WS_URL, OPTIONS))
    
    def connection_changed(conn_info):
        print('Connection state: {}, {}, authenticated: {}'.format(conn_info.state, conn_info.state_string, conn_info.authenticated))

    client.on_ws_connection_changed(connection_changed)

    def on_error(err):
        if err:
            print("Error:\t {}".format(err.message))

    client.on_error(on_error)

    return client
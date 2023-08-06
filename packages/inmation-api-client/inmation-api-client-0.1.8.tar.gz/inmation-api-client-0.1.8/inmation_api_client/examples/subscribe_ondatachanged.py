import asyncio
import time
from inmation_api_client import Client, Options, Item

CLIENT = None

USERNAME = 'user'
PASSWORD = 'pass'
WS_URL = "ws://127.0.0.1:8000/ws"

def main():
    global CLIENT
    _io_loop = asyncio.get_event_loop()
    CLIENT = create_api_client(_io_loop)

    _items_path = "/System/Core/"
    items = [
        Item(_items_path + 'Item01'),
        Item(_items_path + 'Item02'),
        Item(_items_path + 'Item03'),
    ]    

    CLIENT.run_async(
        [
            subscribe_to_data_changes(items)
        ]
    )
    
    _io_loop.run_forever()
    _io_loop.close()

async def subscribe_to_data_changes(items):
    start_time = time.clock()

    def s_cbk(*args):
        """Subscribe to data changes callback"""

        print("\n\n*** Subscribe to data changes\n")
        duration = time.clock() - start_time
        print('Duration is {:.3f} ms\n'.format(duration * 1000))

        err = args[0]
        if err:
            print(err.message)
            return
        else:
            _items = args[1]
            if isinstance(_items, list):
                print("{} - {}".format('Item', 'Value'))
                for item in _items:
                    item_val = item['v'] if 'v' in item else 'No Value'
                    print("{} - {}".format(item['p'], item_val))
    
    await CLIENT.subscribe_to_data_changes(items, s_cbk)

def create_api_client(ioloop):
    client = Client(ioloop)
    ioloop.run_until_complete(client.connect_ws(WS_URL, Options(USERNAME, PASSWORD)))
    
    def on_data_changed(*args):
        err = args[0]
        if err:
            print(err.message)
        else:
            _items = args[1]
            if isinstance(_items, list):
                for item in _items:
                    item_val = item['v'] if 'v' in item else 'No Value'
                    print("{} - {}".format(item['p'], item_val))
    client.on_data_changed(on_data_changed)


    def connection_changed(conn_info):
        print('Connection state: {}, {}, authenticated: {}'.format(conn_info.state, conn_info.state_string, conn_info.authenticated))
    client.on_ws_connection_changed(connection_changed)


    def on_error(err):
        if err:
            print("\nError: {}\n".format(err.message))
    client.on_error(on_error)

    return client

if __name__ == '__main__':
    main()
import asyncio
import time
from random import randint
from inmation_api_client import Client, Options, Item, ItemValue

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
    # Read items
    _io_loop.run_until_complete(read_items_at_once(items))

    write_items = [
        ItemValue(_items_path + 'Item01', randint(1, 2**10)),
        ItemValue(_items_path + 'Item02', randint(1, 2**10)),
        ItemValue(_items_path + 'Item03', randint(1, 2**10)),
    ]

    # Write items
    _io_loop.run_until_complete(write_items_at_once(write_items))

async def read_items_at_once(items):
    start_time = time.clock()

    def read_cbk(*args):
        """read items callback"""

        print("\n\n*** Reading items\n")
        duration = time.clock() - start_time
        print('Read duration is {:.3f} ms\n'.format(duration * 1000))

        err = args[0]
        if err:
            print(err.message)
            return
        else:
            _items = args[1]
            if isinstance(_items, list):
                print("{} - {}".format('Item', 'Value'))
                for item in _items:
                    if 'error' in item:
                        print('Error: {}'.format(item['error']['msg']))
                    else:
                        item_val = item['v'] if 'v' in item else 'No Value'
                        print("{} - {}".format(item['p'], item_val))
    
    await CLIENT.read(items, read_cbk)

async def write_items_at_once(items):
    start_time = time.clock()

    def write_cbk(*args):
        """write items callback"""

        print("\n\n*** Writing items\n")
        duration = time.clock() - start_time
        print('Write duration is {:.3f} ms\n'.format(duration * 1000))

        err = args[0]
        if err:
            print(err.message)
            return
        else:
            _items = args[1]
            if isinstance(_items, list):
                print("{} - {}".format('Item', 'Value'))
                for item in _items:
                    if 'error' in item:
                        print('Error: {}'.format(item['error']['msg']))
                    else:
                        print("{} - {}".format(item['p'], item['v']))
    
    await CLIENT.write(items, write_cbk)

def create_api_client(ioloop):
    client = Client(ioloop)
    ioloop.run_until_complete(client.connect_ws(WS_URL, Options(USERNAME, PASSWORD)))

    def connection_changed(conn_info):
        """ closure """
        print('Connection state: {}, {}, authenticated: {}'.format(conn_info.state, conn_info.state_string, conn_info.authenticated))

    client.on_ws_connection_changed(connection_changed)

    def on_error(err):
        if err:
            print("Error: {}".format(err.message))

    client.on_error(on_error)

    return client

if __name__ == '__main__':
    main()
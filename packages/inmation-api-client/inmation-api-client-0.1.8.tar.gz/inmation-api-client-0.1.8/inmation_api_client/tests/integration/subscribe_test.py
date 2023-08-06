import asyncio
import functools
import time
from random import randint
from .environment import ITEM1, ITEM2, ITEM3, create_api_client
from model import Item

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

async def subscribe_to_data_changes(client, items):
    def s_cbk(*args):
        """Subscribe to data changes callback"""
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
    
    await client.subscribe_to_data_changes(items, s_cbk)

def subscribe_test():
    io_loop = asyncio.get_event_loop()
    client = create_api_client(io_loop)
    client.on_data_changed(on_data_changed)

    items = [
        Item(ITEM1), Item(ITEM2), Item(ITEM3)
    ]

    print('\n*** START subscribe_test\n')
    client.run_async([
         subscribe_to_data_changes(client, items)
    ])
    print('\n*** END subscribe_test\n')
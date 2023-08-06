import time
import asyncio
import functools
from .environment import ITEM1, ITEM2, ITEM3, create_api_client
from model import Item

def read_items(ioloop, client, items):    
    _duration_list = []
    _max_reads = 10    
        
    def read_cbk(*args):
        """read items callback"""
        print('({}) Read duration is {:.3f} ms\n'.format(i, duration * 1000))

        err = args[0]
        if err:
            print(err.message)
        # else:
        #     print(args[1])

    for i in range(_max_reads):
        start_time = time.clock()
        ioloop.run_until_complete(client.read(items, read_cbk))
        duration = time.clock() - start_time
        _duration_list.append(duration)

    dur_list_len = len(_duration_list)
    avg_duration = functools.reduce(lambda x,y: x+y, _duration_list) / dur_list_len
    print("Average duration: {:.3f} ms for {} reads".format(avg_duration * 1000, dur_list_len))

def read_test():
    io_loop = asyncio.get_event_loop()
    client = create_api_client(io_loop)
    items = [
        Item(ITEM1), Item(ITEM2), Item(ITEM3)
    ]

    print('\n*** START read_test\n')
    read_items(io_loop, client, items)
    print('\n*** END read_test\n')
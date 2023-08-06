import time
import asyncio
import functools
from random import randint
from .environment import create_api_client, ITEM1, ITEM2, ITEM3
from model import ItemValue

def write_items(ioloop, client):
    _max_reads = 10
    _duration_list = []
        
    def write_cbk(*args):
        """Write items callback"""
        print('({}) Write duration is {:.3f} ms\n'.format(i, duration * 1000))

        err = args[0]
        if err:
            print(err.message)
            return
        # else:
        #     print(args[1])

    for i in range(_max_reads):
        items = [
            ItemValue(ITEM1, randint(1, 2**10)),
            ItemValue(ITEM2, randint(1, 2**10)),
            ItemValue(ITEM3, randint(1, 2**10)),
        ]
        start_time = time.clock()
        ioloop.run_until_complete(client.write(items, write_cbk))
        duration = time.clock() - start_time
        _duration_list.append(duration)

    dur_list_len = len(_duration_list)
    avg_duration = functools.reduce(lambda x,y: x+y, _duration_list) / dur_list_len
    print("Average duration: {:.3f} ms for {} writes".format(avg_duration * 1000, dur_list_len))

def write_test():
    io_loop = asyncio.get_event_loop()
    client = create_api_client(io_loop)

    print('\n*** START write_test\n')
    write_items(io_loop, client)
    print('\n*** END write_test\n')
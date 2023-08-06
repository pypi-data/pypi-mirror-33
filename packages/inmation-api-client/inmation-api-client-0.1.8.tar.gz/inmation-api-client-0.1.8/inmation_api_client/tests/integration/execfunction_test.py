import asyncio
import functools
import json
import time
from .environment import  create_api_client
from model import Item

async def exec_test(ioloop, client):    
    context = Item('/System/Core/APIContext/WebAPI01')

    start_time = time.clock()
    def exec_function_cbk(*args):
        err = args[0]
        data = args[1]
        if err:
            print(err.message)

        duration = time.clock() - start_time
        print("Result in {:.3f} ms: {}".format(duration*1000, json.dumps(data)))
        
    await client.exec_function(context, 'testlib', 'test', {'name': 'test'}, exec_function_cbk)

def execfunction_test():
    io_loop = asyncio.get_event_loop()
    client = create_api_client(io_loop)

    print('\n*** START execfunction_test\n')
    io_loop.run_until_complete(exec_test(io_loop, client))    
    print('\n*** END execfunction_test\n') 
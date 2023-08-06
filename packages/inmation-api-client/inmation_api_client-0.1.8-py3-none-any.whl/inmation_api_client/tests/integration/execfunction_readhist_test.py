import asyncio
from datetime import datetime, timedelta
import functools
import json
import time
from .environment import ITEM1, ITEM2, ITEM3, create_api_client
from model import Item

async def readhist_test(ioloop, client):
    now = datetime.now() 
    now_minus_month = now + timedelta(-30)
    format = '%Y-%m-%dT%H:%M:%S.000Z'
    start_time = now_minus_month.strftime(format)
    end_time = now.strftime(format)

    context = Item('/System/Core/APIContext/WebAPI01')
    paths = [
        ITEM1, 
        ITEM2,
    ]
    aggregates = ['AGG_TYPE_INTERPOLATIVE', 'AGG_TYPE_RAW']
    farg = {
        "paths": paths[0],
        "startTime": start_time,
        "endTime": end_time,
        "aggregates": aggregates[0],
        "intervals": 10
    }

    def exec_function_cbk(*args):
        err = args[0]
        if err:
            print(err.message)

        print("Result: {}".format(json.dumps(args[1])))
        
    await client.exec_function(context, 'histdata-fetcher', 'fetch', farg, exec_function_cbk)

def execfunction_readhist_test():
    io_loop = asyncio.get_event_loop()
    client = create_api_client(io_loop)
    
    print('\n*** START execfunction_readhist_rest\n')
    io_loop.run_until_complete(readhist_test(io_loop, client))
    print('\n*** END execfunction_readhist_rest\n')
import asyncio
from datetime import datetime, timedelta
import time
from .environment import ITEM1, ITEM2, create_api_client
from model import HistoricalDataItem

def test(ioloop, client):    
    now = datetime.now() 
    now_minus_month = now + timedelta(-30)
    format = '%Y-%m-%dT%H:%M:%S.000Z'

    start_time = now_minus_month.strftime(format)
    end_time = now.strftime(format)

    hdi1 = HistoricalDataItem(ITEM1, "AGG_TYPE_RAW")
    hdi2 = HistoricalDataItem(ITEM2, "AGG_TYPE_RAW")

    num_intervals = 1
    max_req = 5
    
    def rhd_cbk(*args):
        err = args[0]
        if err:
            return print(err.message)
        # else:
        #     print(args[1])

    for i in range(1, max_req + 1):
        print("Number of outstanding req {} of total {}".format(i, max_req))
        ioloop.run_until_complete(client.read_historical_data([hdi1, hdi2], start_time, end_time, num_intervals, rhd_cbk))

def readhistoricaldata_test():
    io_loop = asyncio.get_event_loop()
    client = create_api_client(io_loop)
    
    print('\n*** START readhistoricaldata_test\n')
    test(io_loop, client)
    print('\n*** END readhistoricaldata_test\n')
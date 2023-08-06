import asyncio
from datetime import datetime, timedelta
import time
from inmation_api_client import Client, Options, HistoricalDataItem

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
        HistoricalDataItem(_items_path + 'Item01', "AGG_TYPE_RAW"),
        HistoricalDataItem(_items_path + 'Item02', "AGG_TYPE_RAW"),
    ]

    # Read historical data
    read_historical_data(items)

    _io_loop.run_forever()
    _io_loop.close()

def read_historical_data(items):
    start_time = time.clock()

    now = datetime.now() 
    now_minus_month = now + timedelta(-30)
    format = '%Y-%m-%dT%H:%M:%S.000Z'

    hd_stime = now_minus_month.strftime(format)
    hd_etime = now.strftime(format)

    num_of_intervals = 3

    def rhd_cbk(*args):
        """read historical data callback"""

        print("\n\n*** Reading historical data\n")
        duration = time.clock() - start_time
        print('Read duration is {:.3f} ms\n'.format(duration * 1000))

        err = args[0]
        
        if err:
            print(err.message)
            return
        else:
            _items = args[1]
            if isinstance(_items, dict):             
                print("{} {}{}".format("Item",'\t'*7, "Values"))

                for item in _items['items']:
                    if 'intervals' in item:
                        val = None
                        for num_interval in range(0, num_of_intervals):                      
                            if 'V' in item['intervals'][num_interval]:
                                val = item['intervals'][num_interval]['V']
                            print("{} (Interval {:d}): {}".format(item['p'], num_interval+1, val))
    
    asyncio.ensure_future(CLIENT.read_historical_data(items, hd_stime, hd_etime, num_of_intervals, rhd_cbk))

def create_api_client(ioloop):
    client = Client(ioloop)
    ioloop.run_until_complete(client.connect_ws(WS_URL, Options(USERNAME, PASSWORD)))
    
    def connection_changed(conn_info):
        print('Connection state: {}, {}, authenticated: {}'.format(conn_info.state, conn_info.state_string, conn_info.authenticated))

    client.on_ws_connection_changed(connection_changed)

    def on_error(err):
        if err:
            print("Error\t {}".format(err.message))

    client.on_error(on_error)

    return client

if __name__ == '__main__':
    main()
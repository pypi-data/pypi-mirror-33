import asyncio
from .environment import WS_URL, OPTIONS
from inclient import Client

CLIENT = Client()

def connection_changed(conn_info):
    """ closure """
    print('Connection state: {}, {}, authenticated: {}'.format(conn_info.state, conn_info.state_string, conn_info.authenticated))
CLIENT.on_ws_connection_changed(connection_changed)

def on_error(err):
    if err:
        print("Error {}".format(err.message))
CLIENT.on_error(on_error)

async def test():
    num_conn = 5
    for i in range(1, num_conn+1):
        print("\n({}) Connect to: {}".format(i, WS_URL))
        await CLIENT.connect_ws(WS_URL, OPTIONS)
        print('({}) Disconnect'.format(i))
        await CLIENT.disconnect_ws()

        await asyncio.sleep(2)

def connect_test():    
    io_loop = CLIENT.get_ioloop()
    print('\n*** START connect_test\n')
    io_loop.run_until_complete(test())
    print('\n*** END connect_test\n')
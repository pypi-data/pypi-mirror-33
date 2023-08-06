import asyncio
import json
from inspect import isfunction
from inmation_api_client.model import WSConnectionInfo, AuthenticateRPC, CloseRPC, ExecFunctionRPC, RunScriptRPC, \
    SubscribeRPC, ReadRPC, ReadHistoricalDataRPC, ReadRawHistoricalDataRPC, WriteRPC
from websockets import connect
from websockets.protocol import State
from websockets.exceptions import ConnectionClosed
from inmation_api_client.eventemitter import EventEmitter
from inmation_api_client.error import Error

import logging
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def invoke_callback(cbk, *args):
    """ invoke_callback """
    if isfunction(cbk):
        return cbk(*args)
    
RECONNECT_DELAY_TIME = 1
RECONNECT_DELAY_TIME_AFTER_ERROR = 5
MAX_RECCONNECT_ATTEMPTS_AFTER_ERROR = 2

class WSClient(EventEmitter):
    """Set up the WebSocket client."""
    DEBUG_LOG = False
    
    def __init__(self, ioloop):        
        self._reconnect_delay_time = RECONNECT_DELAY_TIME
        self.auto_reconnect = False
        self._ws = None
        # Connection Info contains e.g. sessionid, state and whether the authentication went well.
        self._connection_info = WSConnectionInfo()
        self._subscription_items = {}
        self.url = None
        self.options = None
        self.ioloop = ioloop or asyncio.get_event_loop()
        self.reconnect_counter = 0

        super().__init__(loop=self.ioloop)

        def process_ready_state_cb(ready_state):
            """ process_ready_state_cb. """
            if self._connection_info.set_ready_state(ready_state):
                self.emit(WSClient.CONNECTIONCHANGED, self._connection_info)

        self._process_ready_state = process_ready_state_cb

    def get_ioloop(self):
        """get the asyncio event loop"""
        return self.ioloop

    @property
    def connection_info(self):
        """ get connection info """
        return self._connection_info

    def _subscribe_req_id_callback(self, reqid, cbk):
        if isfunction(cbk):
            self.once(str(reqid), lambda *args: cbk(*args))

    async def authenticate(self, username, password):
        """Authentication request to the WebSocket server.

        Args:
            username (str): Username
            password (str): Password

        Returns:
            void
        """
        if not isinstance(username, str) or not isinstance(password, str):
            raise Error('No username and/or password specified.')

        msg = AuthenticateRPC(username, password)
        await self.send(msg)

    async def close(self):
        """Close connection to the WebSocket server."""
        self.auto_reconnect = False
        
        if self._ws is not None:
            if isfunction(self.remove_all_listeners):
                self.remove_all_listeners()
            if WSClient.DEBUG_LOG:             
                print('Closing the WebSocket connection')
            await self.send(CloseRPC())
            self._ws.close()

            self._process_ready_state(self._ws.state)

    async def connect(self, url, options):
        """Connect to the WebSocket server.

        Args:
            url (str): URL of the WebSocket
            options (object): Options object
        """

        if not isinstance(url, str):
            raise Error('A WebSocket URL is not specified in the configuration.')

        self.url = url
        self.options = options

        if WSClient.DEBUG_LOG:
            print('Connecting to: {}'.format(self.url))
       
        async def _connect(self):
            """connect to the websocket server."""
            try:
                # Disable asynchronous context manager functionality
                @asyncio.coroutine
                def connect_wrapper(*args, **kwds):
                    return connect(*args, **kwds).__await__()

                # max_size = None disables the size limit of incoming messages
                self._ws = await connect_wrapper(self.url, timeout=options.tim or 10, loop=self.ioloop, max_size=None)
            except OSError as err:
                if err.strerror is not None:
                    return err.strerror
            except Exception as e:
                return str(e)

        _con_res = await _connect(self)

        if self._ws:
            self.onopen(self._ws.state)
        else:
            await self.onerror(Error(_con_res))

        self.auto_reconnect = True

        if options and options.usr and options.pwd:
            await self.authenticate(options.usr, options.pwd)

        try:
            if self._ws is not None:
                msg = await self._ws.recv()
                await self.onmessage(msg)
                if not self._connection_info.authenticated:
                    msg = await self._ws.recv()
                    await self.onmessage(msg)

                return True
        except ConnectionClosed as e:
            await self.onclose(e)

    async def reconnect(self):
        """ reconnect. """
        if not self.auto_reconnect:
            return

        await asyncio.sleep(self._reconnect_delay_time)
        
        print('Re-connecting to: {} ...'.format(self.url))
        await self.connect(self.url, self.options)
        
        while True:
            if not self._connection_info.state_string == WSConnectionInfo.CONNECTEDSTRING \
                and not self._connection_info.authenticated:
                await self.connect(self.url, self.options)
            else:
                break

    def onopen(self, ready_state):
        """ onopen. """
        if WSClient.DEBUG_LOG:
            print('WebSocket onopen')
        # Restore reconnect delay time.
        self._reconnect_delay_time = RECONNECT_DELAY_TIME
        self._process_ready_state(ready_state)

    async def onerror(self, err):
        """ onerror. """
        if WSClient.DEBUG_LOG:
            print('WebSocket onerror: {}'.format(err.message))
        if err:
            if 'Failed to connect' in err.message:
                self._reconnect_delay_time = RECONNECT_DELAY_TIME_AFTER_ERROR
                if self.reconnect_counter <= MAX_RECCONNECT_ATTEMPTS_AFTER_ERROR:
                    self.reconnect_counter += 1
                    await self.reconnect()
                else:
                    self.reconnect_counter = 0
                    raise ConnectionRefusedError('Failed to connect, either the credentials are invalid or the Core service is down.')
            elif 'call failed' in err.message:
                raise ConnectionRefusedError(err.message)

        self.emit(WSClient.ERROR, err.message)

    async def onclose(self, exception):
        """ onclose. """        
        if WSClient.DEBUG_LOG:
            print('WebSocket onclose, message: {}'.format(exception))

        self._process_ready_state(self._ws.state)
        if isfunction(self.remove_all_listeners):
            self.remove_all_listeners()

        if self.auto_reconnect:
            self.emit(WSClient.ERROR, str(exception))
            await self.reconnect()
        else:
            await self.close()

    # all the self.emit() will be invoked asap with ioloop.call_soon()
    async def onmessage(self, msg):
        """ onmessage. """
        if msg is None:
            return
        
        message = json.loads(msg)

        if WSClient.DEBUG_LOG:
            print("Message {}".format(msg))

        err = None
        code = None
        if 'code' in message:
            code = int(message['code'])

        if code < 200 or code > 299 and 'error' in message:
            err_msg = ''
            if 'code' in message['error']:
                err_msg += '\nFailed with Code {:d}'.format(message['error']['code'])
            if 'msg' in message['error']:
                err_msg += ", Message: {}".format(message['error']['msg'])
  
            err = Error(err_msg)

        # Store or wipe Connection Info.
        connection_changed = False
        if 'type' in message and 'data' in message:
            if message['type'] == WSClient.CONNECTION or message['type'] == WSClient.AUTHENTICATION:
                connection_changed = self._connection_info.process_info(message['data'], self._ws.state)

        # Emit Error
        if err is not None:
            if 'type' in message:
                if message['type'] == 'authentication' and message['error']['code'] == 1370:
                    await self.onerror(err)
            self.emit(WSClient.ERROR, err)
        
        # Emit connection_changed on new Connection Info or readyState.
        if connection_changed:
            self.emit(WSClient.CONNECTIONCHANGED, self._connection_info)

        # Emit the whole message
        self.emit(WSClient.MESSAGE, err, message)

        # Emit for those who listens to a specific reqid.
        if 'reqid' in message and 'data' in message:
            self.emit(str(message['reqid']), err, message['data'], code)

        try:
            if str(message['data']['authenticated']).lower() == 'true':
                self._connection_info['_authenticated'] = True
        except:
            pass

        # Emit for those who listens to a specific type.
        if 'type' in message and 'data' in message:
            self.emit(message['type'], err, message['data'])

            # Integrated actions
            if message['type'] == WSClient.AUTHENTICATION:
                await self.subscribe()

        if 'reqid' in message and 'type' in message:
            if message['type'] == WSClient.CONNECTION:
                if self.options and self.options.usr and self.options.pwd:
                    await self.authenticate(self.options.usr, self.options.pwd)

    async def receive_forever(self):
        while True:
            await self.receive_msg()

    async def receive_msg(self):
        try:
            msg = await asyncio.wait_for(self._ws.recv(), timeout=20)
        except asyncio.TimeoutError:
            # No data in x seconds, check the connection
            try:
                pong_waiter = await self._ws.ping()
                await asyncio.wait_for(pong_waiter, timeout=10)
            except:
                # No response to ping in x seconds, reconnect
                await self.reconnect()
        except ConnectionClosed as e:
            await self.onclose(e)
        except Exception as e:
            await self.onerror(Error(str(e)))
        else:
            await self.onmessage(msg)

    async def exec_function(self, context, library_name, function_name, function_arg, cbk, options):
        """Execute function.

        Args:
            context (dict): dict with object like {"p": "/System/Core/Test/Item1"}
            library_name (str): Library Script name.
            function_name (str): Library function name.
            function_arg (dict): Library function arguments packed in a dictionary
            cbk (function): Callback
            options (object): Options object
        Returns:
            void
        """
        function_arg_type = type(function_arg)
        if isinstance(function_arg, list):
            function_arg_type = list
        if not isinstance(function_arg, dict) and function_arg_type is not None:
            return invoke_callback(cbk, Error("Argument 'function_arg' needs to be a dict, got {}".format(function_arg_type)), 'no data')

        msg = ExecFunctionRPC(context, library_name, function_name, function_arg, options)
        ignore_resp = options and options.ign is True

        if not ignore_resp:
            self._subscribe_req_id_callback(msg.reqid, cbk)

        await self.send(msg)

    async def send(self, data):
        """Send a data message.

        Args:
            data (object): Data object which needs to be sent
        Returns:
            void
        """
        if self._ws is not None:
            if self._ws.state == State.OPEN:
                json_data = json.dumps(data)
                if WSClient.DEBUG_LOG:
                    print("Sending: {}".format(json_data))
                
                await self._ws.send(json_data)    
                await self.receive_msg()
            else:
                if WSClient.DEBUG_LOG:
                    print('Unable to send data, connection state is {}'.format(self._connection_info.state_string))

    async def subscribe(self, items=None, _type=None, cbk=None, options=None):
        """ subscribe. """
        if isinstance(items, list) and _type:
            self._subscription_items[_type] = items
            msg = SubscribeRPC(self._subscription_items[_type], _type, options)
            self._subscribe_req_id_callback(msg.reqid, cbk)

            await self.send(msg)
        else:
            types = [
                WSClient.CHILDRENCOUNTCHANGED,
                WSClient.CONFIGURATIONVERSIONCHANGED,
                WSClient.DATACHANGED,
                WSClient.USERSTATECHANGED
            ]
            for ltype in types:
                if ltype in self._subscription_items:
                    items = self._subscription_items[ltype]
                    if items: # check whether the len > 0 if items is a sequence
                        if WSClient.DEBUG_LOG:
                            print("Re-subscribe {:d} items for type: {}".format(len(items), ltype))
                        msg = SubscribeRPC(items, ltype)
                        await self.send(msg)

    async def read(self, items, cbk, options=None):
        """ Read item values.

        Args:
            items ([Item]): list of Item {"p": "/System/Core/Test/Item1"}
            cbk (function): Callback
            options (object): Options object
        Returns:
            void
        """
        if not isinstance(items, list):
            return invoke_callback(cbk, Error('Items is not a list'))

        msg = ReadRPC(items, options)
        self._subscribe_req_id_callback(msg.reqid, cbk)
        await self.send(msg)

    async def read_historical_data(self, items, start_time, end_time, number_of_intervals, cbk, options):
        """Read historical item values

        Args:
            items ([HistoricalDataItem]): list of HistoricalDataItem {
                    "p": "/System/Core/Test/Item1"
                    "aggregate": "AGG_TYPE_RAW"
                }
            start_time (str): Start time in UTC format
            end_time (str): End time in UTC format
            number_of_intervals (int): Number of intervals
            cbk (function): Callback
            options (object): Options object

        Returns:
            void
        """
        if not isinstance(items, list):
            return invoke_callback(cbk, Error('Items is not a list'))

        msg = ReadHistoricalDataRPC(items, start_time, end_time, number_of_intervals, options)
        self._subscribe_req_id_callback(msg.reqid, cbk)
        await self.send(msg)

    async def read_raw_historical_data(self, items, start_time, end_time, page_limit, cbk, options):
        """Read raw historical item values.

        Args:
            items ([Item]): list of Item {"p": "/System/Core/Test/Item1"}
            start_time (str): Start time in UTC format.
            end_time (str): End time in UTC format.
            page_limit (int): The maximum number of item values per page.
            cbk (function): Callback
            options (object): Options object

        Returns:
            void
        """
        if not isinstance(items, list):
            return invoke_callback(cbk, Error('Items is not a list'))

        msg = ReadRawHistoricalDataRPC(items, start_time, end_time, page_limit, options)
        self._subscribe_req_id_callback(msg.reqid, cbk)
        await self.send(msg)

    async def run_script(self, context, script, cbk, options):
        """Run script.

        Args:
            context ([Identity]): list of Identity {"p": "/System/Core/Test/Item1"}
            script (str): Script body
            cbk (function): Callback
            options (options): Options object

        Returns:
            void
        """
        msg = RunScriptRPC(context, script, options)
        # Use callback of send when response message is ignored.
        ignore_resp = options and options.ign is True
        if not ignore_resp:
            self._subscribe_req_id_callback(msg.reqid, cbk)

        await self.send(msg)

    async def write(self, items, cbk, options=None):
        """Write item values.

        Args:
            items ([ItemValue]): list of ItemValue {
                    "p": "/System/Core/Test/Item1",
                    "v": 10.5,
                    "q":  0, // Quality (optional)
                    "t": "2017-06-19T12:41:19.56Z" // timestamp (optional)
                }
            cbk (function): Callback
            options (object): Options object
        Returns:
            void
        """
        if not isinstance(items, list):
            return invoke_callback(cbk, Error('Items is not a list'))

        msg = WriteRPC(items, options)
        # Use callback of send when response message is ignored.
        ignore_resp = options and options.ign is True

        if not ignore_resp:
            self._subscribe_req_id_callback(msg.reqid, cbk)

        await self.send(msg)

WSClient.AUTHENTICATION = 'authentication'
WSClient.CHILDRENCOUNTCHANGED = 'childrencountchanged'
WSClient.CONNECTIONCHANGED = 'connectionchanged'
WSClient.CONFIGURATIONVERSIONCHANGED = 'configurationversionchanged'
WSClient.CONNECTION = 'connection'
WSClient.DATACHANGED = 'datachanged'
WSClient.ERROR = 'error'
WSClient.MESSAGE = 'message'
WSClient.READ = 'read'
WSClient.USERSTATECHANGED = 'userstatechanged'
WSClient.WRITE = 'write'

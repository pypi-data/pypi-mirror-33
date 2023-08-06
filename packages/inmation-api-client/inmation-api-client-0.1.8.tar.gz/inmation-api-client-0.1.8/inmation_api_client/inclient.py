import asyncio
from sys import exit
from inspect import isfunction
from inmation_api_client.wsclient import WSClient

class Client(object):
    """ client class. """
    def __init__(self, ioloop=None):
        #Set up the API Client
        self._ws_client = WSClient(ioloop)

    async def disconnect_ws(self):
        """ Disconnect from the WebSocket server. """
        await self._ws_client.close()

    def get_wsclient(self):
        return self._ws_client

    @staticmethod
    def enable_debug():
        WSClient.DEBUG_LOG = True

    @staticmethod
    def disable_debug():
        WSClient.DEBUG_LOG = False

    def get_ioloop(self):
        return self._ws_client.get_ioloop()

    def run_async(self, tasks=[]):
        if not isinstance(tasks, list):
            raise RuntimeError("The tasks argument must be of type list")
        loop = self.get_ioloop()
        loop.run_until_complete(
            asyncio.wait(
                [self._ws_client.receive_forever()] + tasks
            )
        )

    async def connect_ws(self, url, options):
        """Connect to the WebSocket server.

        Args:
            url (str): URL of the WebSocket
            cbk (function): Callback
            options (object): Options object

        Returns:
            void
        """
        try:
            await self._ws_client.connect(url, options)
        except ConnectionRefusedError as e:
            exit(str(e))

    async def exec_function(self, context, library_name, function_name, function_arg, cbk, options=None):
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
        await self._ws_client.exec_function(context, library_name, function_name, function_arg, cbk, options)

    def on(self, event_name, closure):
        """ on. """
        if not isfunction(closure):
            return
        
        self._ws_client.on(event_name, closure)

    def on_children_count_changed(self, closure):
        """ on_children_count_changed. """
        self.on(WSClient.CHILDRENCOUNTCHANGED, closure)

    def on_config_version_changed(self, closure):
        """ on_configuration_version_changed. """
        self.on(WSClient.CONFIGURATIONVERSIONCHANGED, closure)

    def on_ws_connection_changed(self, closure):
        """ on_ws_connection_changed. """
        self.on(WSClient.CONNECTIONCHANGED, closure)

    def on_data_changed(self, closure):
        """ on_data_changed. """
        self.on(WSClient.DATACHANGED, closure)

    def on_error(self, closure):
        """ on_error. """
        self.on(WSClient.ERROR, closure)

    def on_message(self, closure):
        """ on_message. """
        self.on(WSClient.MESSAGE, closure)

    def on_connection(self, closure):
        """ on_connection. """
        self.on(WSClient.CONNECTION, closure)

    def on_user_state_changed(self, closure):
        """ on_user_state_changed. """
        self.on(WSClient.USERSTATECHANGED, closure)

    async def run_script(self, context, script, cbk, options=None):
        """Run script.

        Args:
            context ([Identity]): list of Identity {"p": "/System/Core/Test/Item1"}
            script (str): Script body
            cbk (function): Callback
            options (options): Options object

        Returns:
            void
        """
        await self._ws_client.run_script(context, script, cbk, options)

    async def read(self, items, cbk, options=None):
        """ Read item values.

        Args:
            items ([Item]]): list of Item {"p": "/System/Core/Test/Item1"}
            cbk (function): Callback
            options (object): Options object
        Returns:
            void
        """
        await self._ws_client.read(items, cbk, options)

    async def read_historical_data(self, items, start_time, end_time, number_of_intervals, cbk, options=None):
        """Read historical item values

        Args:
            items ([HistoricalDataItem]): list of HistoricalDataItem {
                    "p": "/System/Core/Test/Item1"
                    "aggregate": "AGG_TYPE_RAW"
                }
            start_time (str): Start time in UTC format
            end_time (str): Ent time in UTC format
            number_of_intervals (int): Number of intervals
            cbk (function): Callback
            options (object): Options object

        Returns:
            void
        """
        await self._ws_client.read_historical_data(items, start_time, end_time, number_of_intervals, cbk, options)

    async def read_raw_historical_data(self, items, start_time, end_time, page_limit, cbk, options=None):
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
        await self._ws_client.read_raw_historical_data(items, start_time, end_time, page_limit, cbk, options)

    async def subscribe_to_children_count_changes(self, items, cbk):
        """Subscribe to ChildrenCount changed.

        Args:
            items ([Item]): list of Item {"p": "/System/Core/Test/Item1"}
            cbk (function): Callback

        Returns:
            void
        """
        await self._ws_client.subscribe(items, WSClient.CHILDRENCOUNTCHANGED, cbk)

    async def subscribe_to_configuration_version_changes(self, items, cbk):
        """Subscribe to ConfigurationVersion changed.

        Args:
            items ([Item]): list of Item {"p": "/System/Core/Test/Item1"}
            cbk (function): Callback

        Returns:
            void
        """
        await self._ws_client.subscribe(items, WSClient.CONFIGURATIONVERSIONCHANGED, cbk)

    async def subscribe_to_data_changes(self, items, cbk):
        """Subscribe to Data changes.

        Args:
            items ([Item]): list of Item {"p": "/System/Core/Test/Item1"}
            cbk (function): Callback

        Returns:
            void
        """
        await self._ws_client.subscribe(items, WSClient.DATACHANGED, cbk)

    async def subscribe_to_user_state_changes(self, items, cbk):
        """Subscribe to UserState changes.

        Args:
            items ([Item]): list of Item {"p": "/System/Core/Test/Item1"}
            cbk (function): Callback

        Returns:
            void
        """
        await self._ws_client.subscribe(items, WSClient.USERSTATECHANGED, cbk)

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
        await self._ws_client.write(items, cbk, options=None)

    @property
    def ws_connection_info(self):
        """wsConnectionInfo.

        Returns:
            object: WSConnectionInfo with sessionid and autheticated flag
        """
        return self._ws_client.connection_info

from datetime import datetime
from inmation_api_client.data import Data
from websockets.protocol import State

class WSConnectionInfo(dict):
    """ WSConnectionInfo """
    def __init__(self, doc=None):
        super().__init__()
        self['_sessionid'] = None
        self['_authenticated'] = None       
        self['_state'] = None
        self['_state_string'] = ""
        self['_ready_state'] = -1
        self.process_info(doc)

    def process_info(self, info, ready_state=None):
        """ process info. """
        _info = info or None
        changed = False

        def _assign_property(prop_name, default_value=None):
            """ assign property. """
            _prop_name = '_{}'.format(prop_name)
            change = False
            if _info is not None:
                if self[_prop_name] != _info[prop_name]:
                    change = True
            else:
                change = True

            if change:
                nonlocal changed
                changed = True
                if _info is not None:
                    self[_prop_name] = _info[prop_name] or default_value
                else:
                    self[_prop_name] = default_value

        _assign_property('sessionid')
        _assign_property('authenticated', False)

        rs_changed = self.set_ready_state(ready_state, True)

        return changed or rs_changed

    def set_ready_state(self, ready_state, force_update=False):
        """ set ready state """
        if not force_update and self['_ready_state'] == ready_state:
            return False
        self['_ready_state'] = ready_state

        def _set_state(state):
            """ _set_state. """
            self['_state'] = state
            if state == WSConnectionInfo.CONNECTING:
                self['_state_string'] = WSConnectionInfo.CONNECTINGSTRING
            elif state == WSConnectionInfo.OPEN:
                self['_state_string'] = WSConnectionInfo.OPENSTRING
            elif state == WSConnectionInfo.DISCONNECTING:
                self['_state_string'] = WSConnectionInfo.DISCONNECTINGSTRING
            elif state == WSConnectionInfo.CONNECTED:
                self['_state_string'] = WSConnectionInfo.CONNECTEDSTRING
            else:
                self['_sessionid'] = None
                self['_authenticated'] = False
                self['_state_string'] = WSConnectionInfo.DISCONNECTEDSTRING

        if ready_state == State.CLOSED:
            _set_state(WSConnectionInfo.DISCONNECTED)
        elif ready_state == State.CLOSING:
            _set_state(WSConnectionInfo.DISCONNECTING)
        elif ready_state == State.CONNECTING:
            _set_state(WSConnectionInfo.CONNECTING)
        elif ready_state == State.OPEN and self['_sessionid'] != None:
            _set_state(WSConnectionInfo.CONNECTED)
        elif ready_state == State.OPEN:
            _set_state(WSConnectionInfo.OPEN)
        else:
            _set_state(WSConnectionInfo.DISCONNECTED)

        return True

    @property
    def authenticated(self):
        """ property authenticated """
        return self['_authenticated']

    @property
    def sessionid(self):
        """ property sessionid """
        return self['_sessionid']

    @property
    def state(self):
        """ property state """
        return self['_state']

    @property
    def state_string(self):
        """ property state_string """
        return self['_state_string']
# end of WSConnectionInfo class

WSConnectionInfo.CONNECTING = 0
WSConnectionInfo.OPEN = 1
WSConnectionInfo.DISCONNECTING = 2
WSConnectionInfo.DISCONNECTED = 3
WSConnectionInfo.CONNECTED = 4

WSConnectionInfo.CONNECTINGSTRING = 'Connecting'
WSConnectionInfo.OPENSTRING = 'Open'
WSConnectionInfo.DISCONNECTINGSTRING = 'Disconnecting'
WSConnectionInfo.DISCONNECTEDSTRING = 'Disconnected'
WSConnectionInfo.CONNECTEDSTRING = 'Connected'

class Identity(dict):
    """ Identity. """
    def __init__(self, identifier):
        super().__init__()
        if isinstance(identifier, str):
            self['p'] = identifier
        elif isinstance(identifier, int):
            self['i'] = identifier

class Item(Identity):
    """ Item """
    def __init__(self, identifier):
        super().__init__(identifier)

class ItemValue(Item):
    """ ItemValue """
    def __init__(self, path, value, timestamp=None, quality=None):
        super().__init__(path)
        date = datetime.utcnow()

        self['v'] = value
        self['q'] = quality or 0
        self['t'] = timestamp or date.isoformat()      

class HistoricalDataItem(Item):
    """ HistoricalDataItem """
    def __init__(self, identifier, aggregate):
        super().__init__(identifier)
        self['aggregate'] = aggregate

REQID_NUMBER = 0
def reqid():
    """ Request id. """
    global REQID_NUMBER
    # Bigger than this number is inf
    if REQID_NUMBER == 1.79e+308:
        REQID_NUMBER = 0

    REQID_NUMBER += 1
    return REQID_NUMBER

class RPC(dict):
    """ RPC """
    def __init__(self, name, _options=None):
        super().__init__()
        self.name = name
        self.reqid = reqid()
        self.data = Data()
        if _options:
            self.options = _options

    @property
    def name(self):
        return self['name']

    @name.setter
    def name(self, _name):
        self['name'] = _name

    @property
    def data(self):
        return self['data']

    @data.setter
    def data(self, _data):
        self['data'] = _data

    @property
    def reqid(self):
        """ get reqid property """
        return self['reqid']

    @reqid.setter
    def reqid(self, _reqid):
        self['reqid'] = _reqid

    @property
    def options(self):
        """ get options """
        return self['opt']

    @options.setter
    def options(self, options):
        """ set options """
        self['opt'] = options

    def copy_param_to_data(self, params, name, _type):
        """ copy a param to the data object """
        if params is None:
            return
        param_val = params[name]

        if param_val == _type:
            self.data[name] = param_val

class AuthenticateRPC(RPC):
    """ AuthenticateRPC """
    def __init__(self, username, password):
        super().__init__(AuthenticateRPC.NAME)
        self.username = username
        self.password = password

    @property
    def username(self):
        """ get username property """
        return self.data.usr

    @username.setter
    def username(self, username):
        self.data.usr = username

    @property
    def password(self):
        """ get password property """
        return self.data.pwd

    @password.setter
    def password(self, password):
        self.data.pwd = password

class CloseRPC(RPC):
    """ CloseRPC """
    def __init__(self):
        super().__init__(CloseRPC.NAME)

class ItemsRPC(RPC):
    """ ItemsRPC """
    def __init__(self, name, items, options):
        super().__init__(name, options)
        self._items = items

    @property
    def _items(self):
        """ get items property """
        return self.data['items']

    @_items.setter
    def _items(self, items):
        self.data['items'] = items or []

class ReadHistoricalDataRPC(ItemsRPC):
    """ ReadHistoricalDataRPC """
    def __init__(self, histItems, start_time, end_time, number_of_intervals, options):
        super().__init__(ReadHistoricalDataRPC.NAME, histItems, options)
        self.data.start_time = start_time
        self.data.end_time = end_time
        self.intervals_no = number_of_intervals

    @property
    def intervals_no(self):
        """ get intervals_no property """
        return self.data['intervals_no']

    @intervals_no.setter
    def intervals_no(self, intervals_no):
        self.data['intervals_no'] = intervals_no

class ReadRawHistoricalDataRPC(ItemsRPC):
    """ ReadRawHistoricalDataRPC """
    def __init__(self, items, startTime, endTime, page_limit, options):
        super().__init__(ReadRawHistoricalDataRPC.NAME, items, options)
        self.data.start_time = startTime
        self.data.end_time = endTime

        if isinstance(page_limit, int):
            self.data['paging'] = {
                'limit': page_limit
            }

class ReadRPC(ItemsRPC):
    """ ReadRPC """
    def __init__(self, items, options):
        super().__init__(ReadRPC.NAME, items, options)

class RunScriptRPC(RPC):
    """ RunScriptRPC """
    def __init__(self, context, script, options):
        super().__init__(RunScriptRPC.NAME, options)
        self.context = context
        self.data.scr = script

    @property
    def context(self):
        """ get context property """
        return self['ctx']

    @context.setter
    def context(self, context):
        ctx = context
        if not isinstance(context, list) and context is not None:
            ctx = [context]

        self['ctx'] = ctx

    @property
    def script(self):
        """ get script property """
        return self.data.scr

    @script.setter
    def script(self, script):
        self.data.scr = script

class ExecFunctionRPC(RunScriptRPC):
    """ ExecFunctionRPC """
    def __init__(self, context, library_name, function_name, function_arg, options):
        super().__init__(context, None, options)
        self.name = ExecFunctionRPC.NAME
        self.library_name = library_name
        self.function_name = function_name
        self.function_arg = function_arg

    @property
    def function_arg(self):
        """ get function_arg property """
        return self.data.farg

    @function_arg.setter
    def function_arg(self, func_arg):
        self.data.farg = func_arg

    @property
    def function_name(self):
        """ get function_name property """
        return self.data.func

    @function_name.setter
    def function_name(self, func_name):
        self.data.func = func_name

    @property
    def library_name(self):
        """ get library_name property """
        return self.data.lib

    @library_name.setter
    def library_name(self, lib_name):
        self.data.lib = lib_name

class SubscribeRPC(ItemsRPC):
    """ SubscribeRPC """
    def __init__(self, items, _type, options=None):
        super().__init__(SubscribeRPC.NAME, items, options)
        self.type = _type

    @property
    def type(self):
        """ get type property """
        return self.data.type

    @type.setter
    def type(self, _type):
        self.data.type = _type

class WriteRPC(ItemsRPC):
    """ WriteRPC """
    def __init__(self, items, options):
        super().__init__(WriteRPC.NAME, items, options)

AuthenticateRPC.NAME = "authenticate"
CloseRPC.NAME = "close"
ExecFunctionRPC.NAME = "execfunction"
ReadRPC.NAME = "read"
ReadRawHistoricalDataRPC.NAME = "readrawhist"
ReadHistoricalDataRPC.NAME = "readhistoricaldata"
RunScriptRPC.NAME = "runscript"
SubscribeRPC.NAME = "subscribe"
WriteRPC.NAME = "write"
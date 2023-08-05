#
# 
from .constants import Constants
from .logger import Logger
from .base import Base
 
from socketIO_client import SocketIO, BaseNamespace, LoggingNamespace

import uuid

class SocketListener(LoggingNamespace):

    def on_connect(self):
        print('[Connected]')

    def on_reconnect(self):
        print('[Reconnected]')

    def on_disconnect(self):
        print('[Disconnected]')


class Socket(Base):
    
    #
    def __init__(self, host=None, port=None, protocol=None):
        self.type = 'RAW'

        self.autoreconnect = True
        if (host is None):
            self.host = 'localhost'
        else:
            self.host = host

        if (port is None):
            self.port = Constants.DEFAULT_PORT
        else:
            self.port = port

        if (protocol is not None):
            self.protocol = protocol

        self.socket = None
        self.connected = False
        self.id = str(uuid.uuid4())
        self.name = Constants.ANONYMOUS
        self.alias = None

        #
        self.on_connect_listeners = []
        self.on_error_listener = None
        self.on_event_func_list = None

    def __apply_on_events (self):
        if (self.on_event_func_list is not None and len(self.on_event_func_list) > 0):
            map(lambda func : func(), self.on_event_func_list)
            del self.on_event_func_list
            self.on_event_func_list = None

    def send_identification_info(self):
        self.send_message(self.type, {'name': self.name, 'id':self.get_id()})

    def on_connect(self):
        Logger.log("connected to message queue server")

        self.connected = True
        self.socket.on('ERROR', self.__on_error__)

        self.send_identification_info()

        i = 0
        while (i < len(self.on_connect_listeners)):
            listener = self.on_connect_listeners[i]
            listener()
            i += 1

    def on_disconnect(self):
        self.connected = False
        #Logger.debug('disconnect')
        Logger.log("Socket (" + self.get_id() + ") is disconnected")

    def on_reconnect(self):
        Logger.debug('reconnect')

    def on_error(self):
        Logger.error('oops, something wrong.')
        
    #
    # On TYO-MQ ERROR MESSAGE
    #
    def __on_error__(self, msg):
        if (self.on_error_listener is not None):
            self.on_error_listener()
        else:
            Logger.error(msg)

    #
    #
    #
    def connect(self, duration=-1, callback=None, cls=SocketListener, **kw):
        # Example
        # with SocketIO(self.host, self.port, SocketListener) as socketIO:
        #     socketIO.emit('event')
        #     socketIO.wait(seconds=1)
        self.socket = SocketIO(self.host, self.port, cls, kw)
        self.socket.on('connect', self.on_connect if callback is None  else callback)
        self.socket.on('disconnect', self.on_disconnect)
        self.socket.on('reconnect', self.on_reconnect)

        if duration == -1 :
            self.socket.wait()
        else:
            self.socket.wait(seconds=duration)


    def get_id(self):
        return self.id

    def add_on_connect_listener(self, listener):
        self.on_connect_listeners.append(listener)

    def disconnect(self):
        if (self.socket is not None and self.connected):
            self.socket.disconnect()

    def on(self, event, callback):
        if (self.socket is None):
            #raise Exception("Socket is not created yet")
            if self.on_event_func_list is None:
                self.on_event_func_list = []
                futureFunc = lambda : self.__apply_on_events()
                self.add_on_connect_listener(futureFunc)

            self.on_event_func_list.append(callback)
        else: 
            self.socket.on(event, callback)

    def send_message(self, event, msg):
        if (self.socket is None):
            raise Exception("Socket isn't ininitalized yet")

        if (self.socket.connected is False):
            futureFunc = lambda event, msg: self.socket.emit(event, msg)

            if (self.autoreconnect is True):
                    self.connect(-1, futureFunc)
            else:
                raise Exception("Socket is created but not connected")
        else:
            self.socket.emit(event, msg)




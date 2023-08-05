#
#
from .subscriber import Subscriber
from .logger import Logger
from .constants import Constants
from .events import Events

#
import json

class Publisher(Subscriber):
    def __init__(self, name, eventDefault=None, host=None, port=None, protocol=None):
        super(Publisher, self).__init__(name, host, port, protocol)

        self.type = 'PRODUCER'
        self.eventDefault = eventDefault if eventDefault is not None else Constants.EVENT_DEFAULT
        self.on_subscription_listener = None
        self.subscribers = {}

        # // Initialisation
        futureFunc = lambda : self.set_on_subscription_listener()
        self.add_on_connect_listener(futureFunc)

        #
        Logger.debug("creating producer: " + self.name)

    def broadcast (self, data, event=None):
        self.produce(data, event, Constants.METHOD_BROADCAST)
        
    def produce (self, data, event=None, method=None) :   
        if (data is None):
             raise Exception("data can't be null")
        
        if (event is None):
            if (self.eventDefault is None):
                raise Exception("please specifiy event")
            else:
                 event = self.eventDefault   

        message = {"event":event, "message":data, "from":self.name, "method":method}
        self.send_message('PRODUCE', message)     

    # /**
    #  * On Subscribe
    #  */
    def __on_subscription (self, data) :
        Logger.log("Received subscription information: " + json.dumps(data))

        self.subscribers[data["id"]] = data

        # // further listener
        if (self.on_subscription_listener is not None):
            self.on_subscription_listener(data)

    def set_on_subscription_listener (self) :
        event = Events.to_onsubscribe_event(self.get_id())
        self.on(event, self.__on_subscription)

    # /**
    #  * On Lost connections with subscriber(s)
    #  */
    def __on_lost_subscriber (self, callback, data) :
        Logger.log("Lost subscriber's connection")
        if (callback is not None):
            callback(data)

    def set_on_subscriber_lost_listener (self, callback) :
        event = Events.to_ondisconnect_event(self.get_id())
        futureFunc = lambda data : (lambda data, cb=callback : self.__on_lost_subscriber(cb, data))(data)
        self.on(event, futureFunc)

    def on_subscriber_lost (self, callback) : 
        self.set_on_subscriber_lost_listener(callback)

    # /**
    #  * On Unsubsribe
    #  */
    def __on_unsubscribed (self, callback, data) : 
        if callback is not None:
            callback(data)

    def set_on_unsubscribed_listener (self, event, callback) :
        event = Events.to_onunsubscribe_event(event, self.get_id())
        futureFunc = lambda data : (lambda data, cb=callback: self.__on_unsubscribed(cb, data))(data)
        self.on(event, futureFunc)

    def on_unsubscribed (self, event, callback) :
        self.set_on_unsubscribed_listener(event, callback)

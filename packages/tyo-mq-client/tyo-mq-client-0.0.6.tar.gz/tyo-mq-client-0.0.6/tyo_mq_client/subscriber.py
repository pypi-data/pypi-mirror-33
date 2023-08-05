from .socket import Socket
from .logger import Logger
from .events import Events
from .constants import Constants

#
import json, sys

class Subscriber(Socket):

    #
    def __init__(self, name=None, host=None, port=None, protocol=None):
        super(Subscriber, self).__init__(host, port, protocol)

        self.type = 'CONSUMER'
        self.name = name if name is not None else Constants.ANONYMOUS
        self.consumes = None
        self.subscriptions = None
        Logger.debug("creating subscriber: " + self.name)

    # def send_identification_info(self):
    #     self.send_message(, {'name': self.name})

    def __apply_subscritptions(self):
        if (len(self.subscriptions) > 0):
            map(lambda func : func(), self.subscriptions)
            del self.subscriptions
            self.subscriptions = None

    def __trigger_consume_event(self, obj, eventStr, callback) :
        #if obj["event"] == eventStr :
        callback(obj["message"])

    #
    # For debug
    # 
    def __debug_on_message(self, event, message):
        Logger.debug('received message', event, message)
        try:
            func = self.consumes[event]
            self.__trigger_consume_event(message, event, func)
        except :
            Logger.error("Ooops, something wrong", sys.exc_info()[0])
            raise
    #     Logger.debug(event, ":", json.dumps(message))
    #     callback(message)

    # def __debug_on_message(self, *args):
    #     Logger.debug('received message', args)

    def __subscribe_internal(self, who, event, onConsumeCallback):    
            eventStr = None
            if (event is not None):
                eventStr = Events.to_event_string(event)
            else:
                eventStr = who + "-ALL"

            # /**
            #  * @todo
            #  * 
            #  * deal with the ALL events later
            #  */
    
            sendSubscriptionMessage = lambda event=eventStr, who=who, name=self.name : self.send_message('SUBSCRIBE', {"event":event, "producer":who, "consumer":name})

            # // On Connect Message will be trigger by system
            if (self.connected):
                sendSubscriptionMessage()
            else:
                if self.subscriptions is None:
                    self.subscriptions = []
                    futureFunc = lambda : self.__apply_subscritptions()
                    self.add_on_connect_listener(futureFunc)

                self.subscriptions.append(sendSubscriptionMessage)
            # // the connection should be ready before we subscribe the message
            # // self.on('connect', function ()  {
            # //     sendSubscriptionMessage()
            # // })
    
            if (self.consumes is None):
                self.consumes = {}
    
            consumeEventStr = Events.to_consume_event(eventStr)
            self.consumes[consumeEventStr] = onConsumeCallback #lambda message, fromWhom : onConsumeCallback(message, fromWhom)
            #lambda obj : lambda obj, event=eventStr, callback=onConsumeCallback : self.__trigger_consume_event(obj, event, callback)

            #futureFunc = lambda data : (lambda data, event=consumeEventStr: self.consumes[event](data))(data)
            #futureFunc = lambda data, eventStr=consumeEventStr : self.consumes[eventStr](data)
            #DEBUG
            Logger.debug("setting on event: " + consumeEventStr)
            #self.on(consumeEventStr, self.__debug_on_message)
            #futureFunc = lambda data : self.__debug_on_message(data)
            futureFunc = lambda data, event=consumeEventStr : self.__debug_on_message(event, data)
            self.on(consumeEventStr, futureFunc)

    def resubscribeWhenReconnect (self, who, event, onConsumeCallback, reSubscribe=True):

        resubscribeListener = lambda who=who, eventStr=event, callback=onConsumeCallback: self.__subscribe_internal(who, eventStr, callback)

        self.__subscribe_internal(who, event, onConsumeCallback)

        if (reSubscribe is True):
            self.add_on_connect_listener(resubscribeListener)

    # /**
    #  * Subscribe message
    #  * 
    #  * If an event name is not provided, then we subscribe all the messages from the producer
    #  */

    def subscribe (self, who, event, onConsumeCallback, reconcect=True):
        self.resubscribeWhenReconnect(who, event, onConsumeCallback, reconcect)

    # /**
    #  * Subscribe only once, if the connection is gone, let it be
    #  */

    def subscribeOnce (self, who, event, onConsumeCallback):
        self.subscribe(who, event, onConsumeCallback, False)

    # /**
    #  * Subscribe all events with this name whatever providers are publishing
    #  */
    def subscribeAll (self, event, onConsumeCallback):
        self.subscribe(Constants.ALL_PUBLISHERS, event, onConsumeCallback, True)
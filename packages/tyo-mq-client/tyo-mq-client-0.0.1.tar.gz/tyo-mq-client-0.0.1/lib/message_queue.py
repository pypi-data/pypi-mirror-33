#
#
from .constants import Constants
from .publisher import Publisher
from .subscriber import Subscriber
from .socket import Socket
from .events import Events
from .logger import Logger

class MessageQueue(object):

    def __init__(self, host=None, port=None, protocol=None):
        # The SocketIO instance
        if not host is None:
            self.host = host

        if port is not None:
            self.port = port

    @staticmethod
    def createSocket():
        mySocket = Socket()

        return mySocket

    #/**
     #* private function
     #*/
    @staticmethod
    def createConsumerPrivate(name, host=None, port=None, protocol=None): 
        consumer = Subscriber(name, host, port, protocol)
        return consumer


    # /**
    #  * Create a consumer
    #  */
    @classmethod
    def createConsumer(cls, name, host=None, port=None, protocol=None):
        return cls.createConsumerPrivate(name, host, port, protocol)

    # /**
    #  * Alias of createConsumer
    #  */

    def createSubscriber(self, name, host=None, port=None, protocol=None):
        return self.createConsumer(name, host, port, protocol)

    @staticmethod
    def createProducerPrivate (name, eventDefault=None, host=None, port=None, protocol=None):
        producer = Publisher(name, eventDefault, host, port, protocol)
        return producer
     
    # /**
    #  * Create a producer
    #  */
    def createProducer (self, name, eventDefault=None, host=None, port=None, protocol=None):
        return  self.createProducerPrivate(name, eventDefault, host, port, protocol)

    def createPublisher (self, name, eventDefault=None, host=None, port=None, protocol=None):
        return self.createProducer(name, eventDefault, host, port, protocol)
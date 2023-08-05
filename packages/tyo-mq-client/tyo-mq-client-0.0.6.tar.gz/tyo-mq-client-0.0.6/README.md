# tyo-mq-client-python
A TYO-MQ python client for TYO-MQ server.

## TYO-MQ server 
please refer to [TYO-MQ Server]{https://github.com/tyolab/tyo-mq}/server.js

In short, TYO-MQ is an implementation of pub/sub message distribution service using socket.io(webscoket).

### Creating a messaging server

```javascript
var MessageServer = require("tyo-mq").server;

var mq = new MessageServer();
mq.start();
```

### Creating a message producer and consumer

```python
from tyo_mq_client.message_queue import MessageQueue
from tyo_mq_client.socket import Socket
from tyo_mq_client.logger import Logger
from tyo_mq_client.constants import Constants

subscriber = None
producer = None
ready = [False, False]

mq = MessageQueue()

producer = mq.createPublisher("TYO Lab")

# A producer can be also a consumer
subscriber = producer

def on_message_published(message):
    print ("received message" + json.dumps(message))
    os._exit(1)

def check ():
    if (ready[0] and ready[1]):
        producer.produce({"message": "Hello World"})

def subscriber_on_connect () :
    Logger.log("Subscriber is connected")
    ready[0] = True
    subscriber.subscribe(producer.name, Constants.EVENT_DEFAULT, on_message_published, False)
    
def on_subscription (data) :
    print ("received subscription")
    producer.produce({"message1": "Hello World"})
    producer.on('test', on_message_published)
    producer.socket.emit('test')
    producer.produce({"message2": "Hello World"}, producer.eventDefault, Constants.METHOD_BROADCAST)

def producer_on_connect () :
    subscriber_on_connect() 

    Logger.log("Producer is connected")
    ready[1] = True
    producer.on_subscription_listener = on_subscription
    producer.on_subscriber_lost(on_subscriber_lost)

def on_subscriber_lost (data):
    message = json.dumps(data)
    Logger.log('Informed that connection with a subscriber (' + message["consumer"] + ') was lost')

producer.add_on_connect_listener(producer_on_connect)
producer.connect(-1)


```

## Maintainer

[Eric Tang](https://twitter.com/_e_tang) @ [TYO LAB](http://tyo.com.au)
#
#

class Events(object):
    #
    @staticmethod
    def to_event_string(event):
        eventStr = event
        # TODO
        # if (typeof event === 'string') {
        #     eventStr = event
        # }
        # else if (typeof event === 'object' && event.event) {
        #     eventStr = event.event
        # }
        # else 
        #     throw new Error ('Unknown event object: should be a string or object with event string')
        return eventStr

    @classmethod
    def to_consume_event(cls, event):
        eventStr = cls.to_event_string(event)
        return 'CONSUME-' + eventStr

    @staticmethod
    def to_ondisconnect_event(id):
        return 'DISCONNECT-' + id

    @classmethod
    def to_onunsubscribe_event(cls, event, id):
        eventStr = cls.to_event_string(event)
        return 'UNSUBSCRIBE-' + eventStr + '-' + id

    @staticmethod
    def to_onsubscribe_event(id):
        return 'SUBSCRIBE-TO' + ("-" + id if (id is not None) else "")
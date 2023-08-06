from shiftevent.handlers import BaseHandler


class Dummy2(BaseHandler):
    """
    Dummy handler 2
    This is mostly used for testing. The side effect it produces is modifying
    the event payload. Be careful, in reality you should never modify an event
    as they are immutable.
    """

    EVENT_TYPE = 'DUMMY_EVENT'

    def handle(self, event):
        """ Handle event """
        payload = event.payload
        payload['dummy_handler2'] = 'processed'
        event.payload = payload
        return event

    def rollback(self, event):
        """ Rollback event """
        payload = event.payload
        if 'dummy_handler2' in payload:
            del payload['dummy_handler2']

        event.payload = payload
        return event



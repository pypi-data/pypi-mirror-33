from shiftevent.handlers import BaseHandler


class NoType(BaseHandler):
    """
    This handler does not define EVENT_TYPE. It should always fail to
    instantiate. Used for testing
    """

    def handle(self, event):
        """ Handle event """
        pass

    def rollback(self, event):
        """ Rollback event """
        pass



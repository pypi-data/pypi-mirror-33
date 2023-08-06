import abc
from shiftevent import exceptions as x


class BaseHandler(metaclass=abc.ABCMeta):
    """
    Base event handler
    This enforces all event handlers to have a common interface and ensures
    all handlers have access to preconfigured environment objects like
    the database, cache, elastic search etc
    """

    # define event type in your concrete implementation
    EVENT_TYPE = None

    # database instance
    db = None

    # cache service instance
    cache = None

    def __init__(self, db):
        """
        Initializes the handler and gets all required service injected
        :param db: shiftevent.db.Db
        """
        self.db = db

        # check event type defined
        if self.EVENT_TYPE is None:
            msg = 'Event type undefined for handler [{}]'
            raise x.MissingEventType(msg.format(self.__class__))

    def check(self, event):
        """
        Check
        A shorthand to check if handler can support the event type passed in
        to handle/rollback methods.
        :param event: shiftevent.event.Event
        :return: bool
        """
        if event.type != self.EVENT_TYPE:
            msg = 'Event handler {} can\'t support events of this type ({})'
            raise x.UnsupportedEventType(msg.format(self.__class__, event.type))

        return True

    def handle_event(self, event):
        """
        Handle event
        Wraps around user-defined handle method to run a check for
        event type support before actual execution.

        :param event: shiftevent.event.Event
        :return: shiftevent.event.Event
        """
        if not event.id:
            msg = 'Unable to handle unsaved event {}'
            raise x.ProcessingUnsavedEvent(msg.format(event))

        self.check(event)
        return self.handle(event)

    def rollback_event(self, event):
        """
        Rollback event
        Wraps around user-defined rollback method to run a check for
        event type support before actual execution.

        :param event: shiftevent.event.Event
        :return: shiftevent.event.Event
        :return:
        """
        if not event.id:
            msg = 'Unable to roll back unsaved event {}'
            raise x.ProcessingUnsavedEvent(msg.format(event))

        self.check(event)
        return self.rollback(event)

    @abc.abstractmethod
    def handle(self, event):
        """
        Process an event
        This should be implemented in concrete handler. It will get triggered
        once an event is emitted.

        :param event: shiftevent.event.Event
        :return: shiftevent.event.Event
        """
        raise NotImplemented('Implement me in your concrete handler')

    @abc.abstractmethod
    def rollback(self, event):
        """
        Rollback an event
        This should be implemented in concrete handler. It will get triggered
        once a travel back in time is requested and we have to sequentially
        undo events effectively reverting the changes made.

        :param event: shiftevent.event.Event
        :return: shiftevent.event.Event
        """
        raise NotImplemented('Implement me in your concrete handler')

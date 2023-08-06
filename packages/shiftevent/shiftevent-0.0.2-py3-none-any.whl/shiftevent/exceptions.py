class EventException(Exception):
    """ Generic event exception marker """
    pass


class ConfigurationException(EventException, RuntimeError):
    """ Raised when configuration is invalid """
    pass


class DatabaseError(EventException, Exception):
    """ Generic database errors """
    pass


class EventError(DatabaseError, RuntimeError):
    """ Raised when there is an issue with event object """
    pass


class ProcessingUnsavedEvent(EventException, RuntimeError):
    """ Raised when emitting or rolling back  unsaved event"""
    pass


class MissingEventType(EventException, RuntimeError):
    """ Raised when handler implementation doesn't define EVENT_TYPE """
    pass


class UnsupportedEventType(EventException, RuntimeError):
    """ Raised when running a handler with unsupported event type """
    pass


class HandlerInstantiationError(EventException, RuntimeError):
    """ Raised when handlers are defined not as classes """
    pass


class InvalidEvent(EventException, RuntimeError):
    """ Raised when trying to persist invalid event """
    def __init__(self, *args, validation_errors=None, **kwargs):
        self.validation_errors = validation_errors
        super().__init__(*args, **kwargs)




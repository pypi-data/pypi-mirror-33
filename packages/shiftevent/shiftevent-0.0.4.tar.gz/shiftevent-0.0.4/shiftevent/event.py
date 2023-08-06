from datetime import datetime
from shiftevent import exceptions as x
from shiftschema.schema import Schema
from shiftschema import validators
from shiftschema import filters
import json
import copy


class EventSchema(Schema):
    """
    Event schema
    Defines filters and validators for an event
    """
    def schema(self):
        self.add_property('created')
        self.created.add_validator(validators.Required(
            message='An event must have creation date'
        ))

        self.add_property('type')
        self.type.add_filter(filters.Strip())
        self.type.add_filter(filters.Uppercase())
        self.type.add_validator(validators.Required(
            message='An event must have a type'
        ))

        self.add_property('object_id')
        self.object_id.add_filter(filters.Strip())
        self.object_id.add_validator(validators.Required(
            message='An event must have an object id'
        ))

        self.add_property('author')
        self.author.add_filter(filters.Strip())
        self.author.add_validator(validators.Required(
            message='An event must have an author set'
        ))


class Event:
    """
    Event
    Represent single atomic operation.
    """
    # event props, initialized at instance level
    props = dict()

    def __init__(self, *_, **kwargs):
        """
        Instantiate event object
        Can optionally populate itself from kwargs

        :param _: args, ignored
        :param kwargs: dict, key-value pairs used to populate event
        """
        # init props
        self.props = dict(
            id=None,
            created=None,
            type=None,
            author=None,
            object_id=None,
            payload=None,
            payload_rollback=None,
        )

        self.from_dict(kwargs)
        if not self.props['created']:
            self.props['created'] = datetime.utcnow()

    def __repr__(self):
        """ Returns printable representation of an event """
        repr = '<Event id=[{}] created=[{}] type=[{}] object_id=[{}]' \
               ' author=[{}]>'
        return repr.format(
            self.id,
            self.created,
            self.type,
            self.object_id,
            self.author
        )

    def __getattr__(self, item):
        """ Overrides attribute access for getting props """
        if item in self.props:
            return self.props[item]
        return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        """ Overrides attribute access for setting props """
        if key == 'payload':
            self.set_payload(value)
        if key == 'payload_rollback':
            self.set_payload_rollback(value)
        elif key in self.props:
            self.props[key] = value
            return self
        else:
            object.__setattr__(self, key, value)
        return self

    def set_payload(self, payload):
        """
        Set payload
        Accepts a dictionary and encodes it into a json string for persistence.
        Will raise an exception if payload is not a dictionary.
        :param payload: dict
        :return:
        """
        if type(payload) is str:
            try:
                payload = json.loads(payload, encoding='utf-8')
            except json.JSONDecodeError:
                raise x.EventError('Failed to decode payload string')

        if payload and type(payload) is not dict:
            msg = 'Payload must be a dictionary, got {}'
            raise x.EventError(msg.format(type(payload)))
        self.props['payload'] = payload
        return self

    def set_payload_rollback(self, payload):
        """
        Set rollback payload
        Accepts a dictionary and encodes it into a json string for persistence.
        Will raise an exception if payload is not a dictionary.
        :param payload: dict
        :return:
        """
        if type(payload) is str:
            try:
                payload = json.loads(payload, encoding='utf-8')
            except json.JSONDecodeError:
                raise x.EventError('Failed to decode payload string')

        if payload and type(payload) is not dict:
            msg = 'Payload must be a dictionary, got {}'
            raise x.EventError(msg.format(type(payload)))
        self.props['payload_rollback'] = payload
        return self

    def to_dict(self):
        """ Returns dictionary representation of the event """
        return copy.copy(self.props)

    def to_db(self):
        """
        To db
        Returns db representation of event. Same as to dict, but payload is
        stringified to json. Used for persistence.
        :return:
        """
        data = self.to_dict()
        data['payload'] = json.dumps(
            data['payload'],
            ensure_ascii=False
        )
        data['payload_rollback'] = json.dumps(
            data['payload_rollback'],
            ensure_ascii=False
        )
        return data

    def from_dict(self, data):
        """ Populates itself from a dictionary """
        for prop, val in data.items():
            if prop in self.props:
                setattr(self, prop, val)
        return self











from .handlers import Dummy1
from .handlers import Dummy2

default_handlers = dict(

    # dummy handlers
    DUMMY_EVENT=[
        Dummy1,
        Dummy2
    ],
)
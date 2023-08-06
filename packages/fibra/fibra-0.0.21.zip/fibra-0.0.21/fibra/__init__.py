"""
Fibra is a sophisticated scheduler for cooperative tasks.

It's a bit lke Stackless Python. It uses Python generator functions
to create tasks which can be iterated.


"""
from __future__ import absolute_import
from fibra.schedule import *
from fibra.handlers.sleep import Sleep
from fibra.handlers.nonblock import Unblock
from fibra.handlers.tasks import Async, Return, Finished, Suspend, Self
from fibra.handlers.tube import Tube, EmptyTube, ClosedTube
from fibra.handlers.io import Read, Write

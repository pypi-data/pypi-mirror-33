import sys

from .constraints import *
from .fields import *
from .general import *


if 'manage.py' not in sys.argv:
    # Django will not allow to create migrations for the models
    from .invalid_fields import *
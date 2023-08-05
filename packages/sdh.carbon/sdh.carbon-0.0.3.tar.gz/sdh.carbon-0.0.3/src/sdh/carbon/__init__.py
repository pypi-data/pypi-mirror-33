from .conf import settings

from .stream import send, send_buff
from .decorators import *
from .profile import *


def configure(parent):
    """
    Bind settings to upstream application main config
    """
    settings.set_parent(parent)

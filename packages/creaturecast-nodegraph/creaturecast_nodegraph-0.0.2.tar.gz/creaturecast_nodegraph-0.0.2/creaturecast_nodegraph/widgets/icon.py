from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import creaturecast_nodegraph.media as media

icon_cache = dict()
import os

def get_icon(key):
    if key in icon_cache:
        return icon_cache[key]
    else:
        icon_path = media.get_icon_path(key)
        if not os.path.exists(icon_path):
            icon_path = media.get_icon_path('empty')
        new_icon = QIcon(icon_path)
        icon_cache['key'] = new_icon
        return new_icon

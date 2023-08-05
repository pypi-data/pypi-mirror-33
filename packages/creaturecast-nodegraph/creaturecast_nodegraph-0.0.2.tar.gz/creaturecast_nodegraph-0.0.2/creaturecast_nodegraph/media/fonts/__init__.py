import os
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

fonts_directory = os.path.dirname(__file__.replace('\\', '/'))

font_cache = dict()

def get_font(*args):
    if args[0] in font_cache:
        return font_cache[args[0]]
    for item in os.listdir(fonts_directory):
        if item == '%s.otf' % args[0]:
            QFontDatabase.addApplicationFont('%s/%s' % (fonts_directory, item))
            font = QFont(*args)
            font_cache[args[0]] = font
            return font


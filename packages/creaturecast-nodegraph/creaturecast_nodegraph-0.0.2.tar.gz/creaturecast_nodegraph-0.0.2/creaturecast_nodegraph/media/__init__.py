import os
import creaturecast_nodegraph
root_package_directory = os.path.dirname(creaturecast_nodegraph.__file__.replace('\\', '/'))
icon_directory = '%s/media/icons' % root_package_directory
image_directory = '%s/media/images' % root_package_directory

def get_icon_path(key):
    return '%s/%s.png' % (icon_directory, key)

def get_image_path(key):
    return '%s/%s.png' % (image_directory, key)

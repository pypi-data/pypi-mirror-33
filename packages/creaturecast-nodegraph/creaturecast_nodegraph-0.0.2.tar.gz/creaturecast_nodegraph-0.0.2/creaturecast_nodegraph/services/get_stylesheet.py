import os
import requests
import json
import shutil
from os.path import expanduser
import creaturecast_nodegraph.services as svc

home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%screaturecast' % home_directory
stylesheets_directory = '%s/stylesheets' % creaturecast_directory


def get_stylesheet(stylesheet, always_download=False):

    stylesheet_path = '%s/%s.qss' % (stylesheets_directory, stylesheet)
    if os.path.exists(stylesheet_path) and not always_download:
        with open(stylesheet_path, mode='r') as f:
            return f.read()

    url = '%s/get_stylesheet' % svc.library_url

    data = dict(stylesheet=stylesheet)

    response = requests.post(
        url,
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'},
        stream=True
    )
    if response.status_code == 200:
        dirname = os.path.dirname(stylesheet_path)
        try:
            os.makedirs(dirname)
        except:
            pass
        stylesheet_text = response.text
        with open(stylesheet_path, 'w') as f:
            f.write(stylesheet_text)
        return stylesheet_text


if __name__ == '__main__':
    print get_stylesheet('slate')

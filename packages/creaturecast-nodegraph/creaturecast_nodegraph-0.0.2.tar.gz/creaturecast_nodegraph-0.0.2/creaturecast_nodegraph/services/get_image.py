import os
import requests
import json
import shutil
import creaturecast_environment as env

creaturecast_directory = env.creaturecast_directory

variation_locations = {
        '128': '/images/icons_128'
    }


def get_image(local_path, always_download=False, variation=None):

    url = '%s/get_image' % env.server_url

    if '/' not in local_path:
        local_path = '/images/icons/%s.png' % local_path

    if variation in variation_locations:
        local_path = '%s/%s' % (variation_locations[variation], local_path.split('/')[-1])
    data = dict(local_path=local_path)


    path = '%s%s' % (creaturecast_directory, local_path)
    if os.path.exists(path) and not always_download:
        return path
    else:
        response = requests.post(
            url,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
            stream=True
        )
        if response.status_code == 200:
            dirname = os.path.dirname(path)
            try:
                os.makedirs(dirname)
            except:
                pass
            with open(path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
                return path
        else:
            raise Exception('Get Image Failed')


if __name__ == '__main__':
    get_image('/python.png')
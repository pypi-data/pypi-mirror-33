import os
import json

from .io import open_file


def load_json(path):
    return json_load(path)


def json_load(path):
    mode = 'r'

    _, ext = os.path.splitext(path)
    if ext == '.gz':
        mode += 't'

    with open_file(path, mode) as f:
        return json.load(f)


def json_dump(obj, path):
    mode = 'w'

    _, ext = os.path.splitext(path)
    if ext == '.gz':
        mode += 't'

    with open_file(path, mode) as f:
        return json.dump(obj, f)

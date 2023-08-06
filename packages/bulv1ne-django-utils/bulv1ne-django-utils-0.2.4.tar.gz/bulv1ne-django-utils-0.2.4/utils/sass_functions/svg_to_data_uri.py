import os
from base64 import b64encode
from urllib.parse import quote


def g_b64(data):
    return b''.join([
        b'data:image/svg+xml;base64,',
        b64encode(data.encode('utf-8'))
    ])


def g_uri(data):
    return ''.join([
        'data:image/svg+xml;charset=UTF-8,',
        quote(data)
    ])


def svg_to_data(data):
    d_b64 = g_b64(data)
    d_uri = g_uri(data)
    if len(d_b64) > len(d_uri):
        return d_uri
    return d_b64


def svg_to_data_uri(file_path, include_paths):
    for path in include_paths:
        try:
            with open(os.path.join(path, file_path)) as f:
                return svg_to_data(f.read())
        except FileNotFoundError:
            pass
    raise FileNotFoundError(file_path)

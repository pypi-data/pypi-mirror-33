import http.client
import json
import os
import sys
import psutil

# To enable debug logging, in your client uncomment this
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CONN = "zoo.trintel.co.za"
HEADERS = {
    'content-type': "application/json",
    'cache-control': "no-cache"
}
URI = "/api/v3/tokens/myip/"


# Possible boolean values in the configuration.
BOOLEAN_STATES = {
    '1': True, 'yes': True, 'true': True, 'on': True,
    '0': False, 'no': False, 'false': False, 'off': False, 'none': False
}


def convert_to_boolean(value):
    """
    Return a boolean value translating from other types if necessary.
    """
    v = str(value).lower()
    if v not in BOOLEAN_STATES:
        raise ValueError('Not a boolean: %s' % value)
    return BOOLEAN_STATES[v]


def get_my_ip():
    error = None
    result = {
        'ip_trusted': 'Read Error',
        'ip_basic': 'Read Error'
    }
    try:
        conn = http.client.HTTPSConnection(CONN)
        conn.request("GET", URI, headers=HEADERS)
        res = conn.getresponse()
        data = res.read()
        try:
            result = json.loads(data.decode("utf-8"))
        except json.decoder.JSONDecodeError as x:
            error = x
    except Exception as x:
        error = x
    return result, error


def safe_get(dct, *keys):
    """
    Just a utility to get values deep in a dictionary.
    :param dct:
    :param keys:
    :return:
    """
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


def restart_program():
    """
    Restarts the current program, with file objects and descriptors
    cleanup
    """
    try:
        p = psutil.Process(os.getpid())
        for handler in p.open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logger.error(e)
    python = sys.executable
    os.execl(python, python, *sys.argv)

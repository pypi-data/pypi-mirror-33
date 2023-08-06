import time
import logging
from . import Client
import logging
import json
import io
import os
import bencode
import requests
try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError


def get_torrent_dir(datastore=None, name=None):
    if not datastore:
        datastore = os.getcwd() + "/datastore/"
    elif datastore == ".":
        datastore = "./"
    elif datastore[-1] != "/":
        datastore = datastore + "/"
    elif datastore[0] != "/":
        datastore = os.getcwd() + "/" + datastore
    if not name:
        return datastore
    if isinstance(name, str):
        name = name.strip("/")
    return datastore + name + '/'

def get(hash, datastore=None, name=None):
    torrent_dir = get_torrent_dir(datastore, name)
    #TODO: remove this contents business, just make these ensure that the torrent exists
    contents = get_from_url(hash, torrent_dir)
    if not contents:
        contents = get_from_file(hash, torrent_dir)
    path = Client.Client(hash, torrent_dir).start()
    return path

def get_from_file(hash, torrent_dir):
    torrent_path = os.path.join(torrent_dir, hash + '.torrent')
    contents = bencode.decode(open(torrent_path, 'rb').read())
    return contents

def get_from_url(hash, torrent_dir):
    contents = None
    try:
        url = "http://academictorrents.com/download/" + hash
        torrent_path = os.path.join(torrent_dir, hash + '.torrent')
        if not os.path.isdir(torrent_dir):
            os.makedirs(torrent_dir)
        response = urlopen(url).read()
        open(torrent_path, 'wb').write(response)
        contents = bencode.decode(open(torrent_path, 'rb').read())
    except Exception as e:
        print("could not download the torrent")
    return contents

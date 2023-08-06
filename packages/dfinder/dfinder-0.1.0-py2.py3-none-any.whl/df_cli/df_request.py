# -*- coding: utf-8 -*-

"""Interface to Dockerfinder"""

import os
import requests


DF_HOST = 'http://black.di.unipi.it'
DF_SEARCH = ':3000/search'

def search_images(query):
    df_host = os.environ.get('DOCKERFINDER_HOST', DF_HOST)
    try:
        json = _request(df_host, DF_SEARCH, query)
        return json['count'], json['images']
    except KeyError:
        raise Exception('Dockerfinder server error.')

def _request(df_host, endpoint, params=None):
    url = df_host + endpoint
    if params is None:
        params = {}
    try:
        ret = requests.get(url, params=params,
                           headers={'Accept': 'applicaiton/json',
                                    'Content-type': 'application/json'},
                           timeout=5)
    except requests.exceptions.RequestException:
        raise Exception('Dockerfinder not responding.')
    return ret.json()

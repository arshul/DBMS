# -*- coding: utf-8 -*-
import requests
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json


def nlu_parser(query):
    q = query.replace("\n", "")

    url = 'http://192.168.1.102:5000/parse'
    post_fields = {'q': q,
                   "project": "TDG13",
                   "model": "Conveyor"
                   }  # Set POST fields here
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, json=post_fields, headers=headers)
    c = r.content
    result = json.loads(c)
    # request = Request(url, urlencode(post_fields).encode())
    # json = urlopen(request).read().decode()
    return result
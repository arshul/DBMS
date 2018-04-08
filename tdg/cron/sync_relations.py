# -*- coding: utf-8 -*-
__author__ = 'himanshujain.2792'

import requests
from flask_script import Command
from tdg.model.model import Channel
from tdg.constants.sender import SENDERS_MAPPING
from tdg.constants.url import URLS
from tdg import app


SENDER_ID = app.config['SENDER_ID']


class Sync(Command):
    def run(self):
        req = requests.get(URLS['get_channel'], params={'consumer_key': SENDERS_MAPPING[SENDER_ID]}).json()

        relations_channel_id = req['result'][0]['id']
        channels = Channel.query.filter_by(group=False).all()
        for channel in channels:
            req_obj = {
                "account_id": str(channel.id),
                "phone": str(channel.number),
                "organisation": channel.company,
                "email": channel.email,
                "name": channel.name,
                "platform": 4,
                "channel_id": relations_channel_id
            }
            print(req_obj)
            req = requests.post(URLS['post_user'], json=req_obj)
            req.json()

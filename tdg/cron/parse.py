# -*- coding: utf-8 -*-
__author__ = 'himanshujain.2792'

import os
import re
from flask_script import Command
from tdg.constants.country_code import COUNTRY_CODE
from tdg.lib.parser import ParserWhatsapp
from tdg.model.model import Channel, Group
from tdg.utils.utility import extract_message_content, extract_phone, is_number, \
    add_message_in_db, add_channel_in_db
from tdg import app

SENDER_ID = app.config['SENDER_ID']


class WhatsappParser(Command):
    def run(self):
        f = []

        for (dirpath, dirnames, filenames) in os.walk(os.getcwd()+'/data'):
            f.extend(filenames)
        for filename in filenames[1:]:
            emoji_pattern = re.compile(
                u"(\ud83d[\ude00-\ude4f])|"  # emoticons
                u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
                u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
                u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
                u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
                "+", flags=re.UNICODE)

            name = re.sub("WhatsApp Chat with ", "", filename)
            name = re.sub(".txt", "", name)
            name = (emoji_pattern.sub(r'', name))  # no emoji
            name = (re.sub("□", "", name))
            group = Channel.query.filter_by(name=name.strip()).first()

            if group:

                with open(os.getcwd()+'/data/'+filename, "r") as fileObj:
                    raw_messages = fileObj.readlines()

                    p = ParserWhatsapp(raw_messages)
                    messages = p.parse()

                    for message in messages:
                        data_dict = extract_message_content(message['message'])

                        if is_number(message['sender']):

                            ph = extract_phone(message['sender'].strip())
                            if not ph['number']:
                                if COUNTRY_CODE.get(message['sender'][:3], None):
                                    ph['number'] = message['sender'][3:]
                                    ph['isd_code'] = message['sender'][1:3]
                                elif COUNTRY_CODE.get(message['sender'][:4], None):
                                    ph['number'] = message['sender'][4:]
                                    ph['isd_code'] = message['sender'][1:4]
                            channel = Channel.query.filter_by(number=ph['number']).first()
                            if not channel:
                                channel_obj = {
                                    'number': ph['number'],
                                    'isd_code': ph['isd_code'],
                                    'name': None,
                                    'group': False,
                                    'alternate_numbers': data_dict['number'],
                                    'website': data_dict['website'],
                                    'email': data_dict['email'],
                                    'sender_id': SENDER_ID
                                }
                                channel = add_channel_in_db(channel_obj)

                        else:
                            channel = Channel.query.filter_by(name=message['sender']).first()

                        if data_dict['group_link'] and channel:
                            if not Group.query.filter_by(link=data_dict['group_link']).all():
                                Group(link=data_dict['group_link'], channel_id=channel.id).save()
                        if channel:
                            data_dict['text'] = message['message']
                            data_dict['sent_date'] = message['sent_date']
                            add_message_in_db(group, channel, data_dict, SENDER_ID)
                        # else:
                        #     print(data_dict)
                        #     print(message)
            else:
                print(name)
                print(filename)
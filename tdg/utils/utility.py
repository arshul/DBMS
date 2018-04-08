# -*- coding: utf-8 -*-

import hashlib
import re
from sqlalchemy.exc import IntegrityError
from tdg.constants.groups import KEYWORDS, REMOVE_LIST
from tdg.model.model import Channel
from tdg.model.message import Message, MessageState
from tdg import logging, db


def extract_message_content(msg):
    website = re.findall(
        r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})",
        msg)
    email = re.findall(
        r"""(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-zA-Z0-9-]*[a-zA-Z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""",
        msg)
    phn = re.findall(r'(?:\+\s*\d{2}[\s-]*)?(?:\d[-\s]*){10}', msg)

    typ = 3
    category = 9
    altered_msg = alter(msg, phn, email, website)
    # for v in KEYWORDS['vendor']:
    #     if re.search(v, msg, re.IGNORECASE):
    #         typ = 1
    # if not typ:
    #     for c in KEYWORDS['client']:
    #         if re.search(c, msg, re.IGNORECASE):
    #             typ = 2
    group_link = None
    if website and re.findall(r"//chat.whatsapp\.com/", website[0]):
        group_link = website[0]
        website = []

    for key in KEYWORDS:
        for word in KEYWORDS[key]['words']:
            if re.search(word, msg, re.IGNORECASE):
                typ = KEYWORDS[key]['type']
                category = KEYWORDS[key]['category']
                continue

    hsh = create_hash(altered_msg)
    data = {'website': website[0] if website else None,
            'email': email[0] if email else None,
            'number': ",".join(phn) if phn else None,
            'hash': hsh,
            'altered_msg': altered_msg,
            'type': typ,
            'category': category,
            'group_link': group_link
            }
    return data


def alter(msg, phone=[], email=[], website=[]):
    text = ""
    for ph in phone:
        msg = msg.replace(ph, "")
    for e in email:
        msg = msg.replace(e, "")
    for w in website:
        msg = msg.replace(w, "")
    for c in REMOVE_LIST:
        flag = False
        if re.search(c, msg, re.IGNORECASE):
            flag = True
            for x in msg.split('\n'):
                if not re.search(c, x, re.IGNORECASE):
                    if not x == '':
                        text = text + x + '\n'
            return text
    if not flag:
        for i in msg.split('\n'):
            if not i == '':
                text = text + i + '\n'
        return text


def create_hash(text):
    hsh = hashlib.md5(text.encode('utf-8')).hexdigest()
    return hsh


def extract_phone(number):
    ph = number.replace('-', ' ').replace('+', ' ').split()
    return {'isd_code': ph[0], 'number': "".join(ph[1:])}


def get_number(msg):
    phn = re.findall(r'(?:\+\s*\d{2}[\s-]*)?(?:\d[-\s]*){10}', msg)
    return phn[0] if phn else None


def is_number(input_val):
    input_val = input_val.replace(" ", "")
    if input_val[1:].isnumeric() and len(input_val[1:]) == 12:
        return True


def add_channel_in_db(channel_obj):
    channel = None
    try:
        channel = Channel(**channel_obj).save()
    except IntegrityError:
        db.session.rollback()
        channel_obj['name'] = None
        try:
            channel = Channel(**channel_obj).save()
        except Exception as exp:
            logging.exception(exp)
    except Exception as exp:
        logging.exception(exp)
    return channel


def add_message_in_db(group, channel, data_dict, sender_id):
    mes = {
        'category': data_dict['category'],
        'hash': data_dict['hash'],
        'text': data_dict['text'],
        'type': data_dict['type']
    }
    m = Message.query.filter_by(hash=data_dict.get('hash')).first()
    if not m:
        message = Message(**mes).save()
        mes_state = {
            'channel_id': channel.id,
            'group_id': group.id if group.group else None,
            'message_id': message.id,
            'sent_date': data_dict['sent_date'],
            'status': 6,
            'hash': data_dict['hash'],
            'sender_id': sender_id
        }

        MessageState(**mes_state).save()

    else:
        if group.group:
            hash_text = str(channel.id) + str(group.id) + str(m.id) + str(data_dict['sent_date'])
        else:
            hash_text = str(channel.id) + str(m.id) + str(data_dict['sent_date'])
        mesg_state_hash = create_hash(hash_text)
        ms = MessageState.query.filter_by(hash=mesg_state_hash).first()
        if not ms:
            mes_state = {
                'channel_id': channel.id,
                'group_id': group.id if group.group else None,
                'message_id': m.id,
                'sent_date': data_dict['sent_date'],
                'status': 6,
                'hash': mesg_state_hash,
                'sender_id': sender_id
            }

            MessageState(**mes_state).save()
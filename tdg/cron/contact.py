# -*- coding: utf-8 -*-
__author__ = 'himanshujain.2792'

import csv
import re
from flask_script import Command
from tdg.constants.country_code import COUNTRY_CODE
from tdg.model.model import Channel
from tdg.utils.utility import add_channel_in_db


class DownloadChannel(Command):
    def run(self):
        channels = Channel.query.filter(Channel.group == False).all()
        print(channels)
        with open('contacts.csv', 'w') as csvfile:
            fieldnames = [
                'Name', "Subject", 'Notes',
                'Phone 1 - Type', 'Phone 1 - Value',
                'E-mail 1 - Type',
                'E-mail 1 - Value', 'Website 1 - Type', 'Website 1 - Value',
                'Group Membership',
                'Organization 1 - Type', 'Organization 1 - Name'
                ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for channel in channels:
                writer.writerow({
                    "Name": channel.name, "Subject": "",
                    "Phone 1 - Type": "Mobile",
                    "Phone 1 - Value": "+"+str(channel.isd_code)+str(channel.number),
                    "Group Membership": "* My Contacts",
                    "E-mail 1 - Type": "* Work", "Website 1 - Type": "Work",
                    "E-mail 1 - Value": channel.email, "Website 1 - Value": channel.website,
                    "Notes": '',
                    "Organization 1 - Type": "Work",
                    "Organization 1 - Name": channel.company
                    })
                # writer.writerow([channel.name, channel.number])


class UploadChannel(Command):
    def run(self):
        with open('google.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            ph = {}
            for row in reader:
                
                if COUNTRY_CODE.get(row['Phone 1 - Value'][:3], None):
                    ph['number'] = row['Phone 1 - Value'][3:]
                    ph['isd_code'] = row['Phone 1 - Value'][1:3]
                elif COUNTRY_CODE.get(row['Phone 1 - Value'][:4], None):
                    ph['number'] = row['Phone 1 - Value'][4:]
                    ph['isd_code'] = row['Phone 1 - Value'][1:4]
                else:
                    print(row['Phone 1 - Value'])
                    continue
                channel = Channel.query.filter_by(number=ph['number']).first()
                if not channel:
                    channel_obj = {
                        'number': ph['number'],
                        'isd_code': ph['isd_code'],
                        'name': row['Name'] if row['Name'] else None,
                        'group': False,
                        'company': row['Organization 1 - Name'] if row['Organization 1 - Name'] else None,
                        'website': row['Website 1 - Value'] if row['Website 1 - Value'] else None,
                        'email': row['E-mail 1 - Value'] if row['E-mail 1 - Value'] else None
                    }
                    add_channel_in_db(channel_obj)
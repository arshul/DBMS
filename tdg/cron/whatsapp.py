# -*- coding: utf-8 -*-
from flask_script import Command
from tdg.lib.whatsapp import Whatsapp
import time
import csv


class WhatsappData(Command):
    def run(self):
        count = 0
        driver = Whatsapp()
        time.sleep(10)
        """         get list of all channel        """
        # channels = driver.get_channels_bytype('user')
        # channels = list(set(channels))
        
        """        Create list of channels       """
        # with open('distributor.csv', 'r') as csvfile:
        #     reader = csv.DictReader(csvfile)
        #     ph = {}
        #     channels = []
        #     for row in reader:
        #         channels.append(row['Contact'])
        channels = ['9210638305', '9210903503']
        message_text = """
Hello
"""
        print(channels)
        driver.message_broadcast(message_text, channels)
        exit()
        channels = driver.get_channels_bytype()
        driver.add_group_channels(channels)
        """    get channels based on sender_id   """
        # channels = driver.get_mapped_channels()

        while True:
            """      Extract Group Contacts       """
            # for c in channels:
            #    driver.extract_group_contacts(c)

            """     extract unread messages        """
            # for c in channels:
            #     driver.extract_unread_messages(c)

            """     float promotional messages    """
            # driver.float_msg()
            driver.send_messages()
            """   extract complete group from the first conversation    """
            # for c in channels:
            #     driver.extract_complete_group(c)

            print("sleeping...")
            time.sleep(20)
            count += 1
            print(count)

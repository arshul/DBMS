# -*- coding: utf-8 -*-

import urllib.request
import os
import time
import requests
import platform
import pyperclip
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from sqlalchemy import or_
from tdg.constants.message import HEADER, FOOTER, DEMAND_ACK, SUPPLY_ACK
from tdg.constants.url import URLS
from tdg.constants.sender import SENDERS_MAPPING
from tdg.model.model import Channel, Group
from tdg.model.message import Message, MessageState
from tdg.utils.timer import get_timestamp
from tdg.utils.utility import extract_message_content, extract_phone, get_number, add_message_in_db,\
    add_channel_in_db
from tdg import app, logging, tdg_tz


SENDER_ID = app.config['SENDER_ID']

CLASSES = {
    'chat_contact': 'default-user',
    'left_panel': '.chatlist-panel-body'
}
IDS = {
    'chatlist_search': 'input-chatlist-search'
}

class Whatsapp():
    _URL = "http://web.whatsapp.com"
    _chrome_options = webdriver.ChromeOptions()
    _chrome_options.add_argument("--disable-infobars")
    _firefox_profile = webdriver.FirefoxProfile()
    _firefox_profile.set_preference("browser.privatebrowsing.autostart", True)

    def __init__(self):
        try:
            if platform.system() == 'Darwin':
                self.driver = webdriver.Firefox(firefox_profile=self._firefox_profile)
            else:
                self.driver = webdriver.Firefox(executable_path=os.path.realpath('') + '/geckodriver')
        except Exception as e:
            print(e)
            self.driver = webdriver.Chrome('chromedriver', chrome_options=self._chrome_options)

        self.driver.get(self._URL)

        while not self.driver.find_elements_by_css_selector('.copyable-text.selectable-text'):
            time.sleep(2)
        self.search_bar = self.driver.find_element_by_id(IDS['chatlist_search'])

    def get_qr(self):
        qr = self.driver.find_element_by_css_selector(".qrcode")
        html = BeautifulSoup(qr.get_attribute('innerHTML'), "html.parser")
        img = html.find("img", {"alt": "Scan me!"})
        urllib.request.urlretrieve(img['src'], "image.png")
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".qrcode > img:nth-child(4)")))

    def acknowledge(self, number, msg, type):
        try:
            persons = self.driver.find_elements_by_css_selector(".RZ7GO")
            for p in persons:
                if p.text == number:
                    p.click()
                    time.sleep(3)
                    msg_box = self.driver.find_element_by_css_selector(
                        '.pluggable-input-body.copyable-text.selectable-text')
                    msg_box.click()
                    msg_box.clear()
                    if type == 1:
                        self.copy_paste_message("Your Cab Info: *{0}* \n\n".format(msg) + SUPPLY_ACK)

                    if type == 2:
                        self.copy_paste_message("Your Query: *{0}* \n\n".format(msg) + DEMAND_ACK)

                    if app.config['SEND_ACKNOWLEDGEMENT']:
                        # msg_box.send_keys(Keys.ENTER)
                        add_channel_in_db(number)
                        break
        except Exception as e:
            logging.exception(e)

    def float_msg(self):
        before_time = datetime.now(tdg_tz) - timedelta(hours=24)
        current_time = datetime.now(tdg_tz)

        messages = MessageState.query.filter(MessageState.status == 1,
                                             MessageState.sender_id == SENDER_ID,
                                             MessageState.schedule_date < current_time,
                                             MessageState.schedule_date >= before_time).\
            order_by(MessageState.schedule_date).all()
        print(messages)
        for message in messages:
            self.search_bar.clear()
            if message.group_id:
                self.search_bar.send_keys(message.group.name)
            else:
                self.search_bar.send_keys(message.channel.number)

            chat_panel = self.driver.find_element_by_css_selector('.' + CLASSES['left_panel'])
            bs = BeautifulSoup(chat_panel.get_attribute('innerHTML'), "html.parser")
            print(bs.find("div", {"class": "chat-drag-cover"}))
            if bs.find("div", {"class": "chat-drag-cover"}):
                try:
                    self.search_bar.send_keys(Keys.ENTER)
                    msg_box = self.driver.find_element_by_css_selector(
                        '.pluggable-input-body.copyable-text.selectable-text')
                    msg_box.click()
                    time.sleep(2)
                    msg_box.clear()
                    self.copy_paste_message(message.message.text)
                    time.sleep(2)
                    if app.config['SEND_MSG']:
                        msg_box.send_keys(Keys.ENTER)
                        message.sent_date = datetime.now()
                        message.status = 2
                        message.update()

                except Exception as e:
                    logging.exception(e)
            else:
                print("number not found in whatsapp")
                phone = str(message.channel.isd_code) + str(message.channel.number)
                self.send_message_noncontacts(phone, message.message.text)
                time.sleep(2)
                while True:
                    try:
                        msg_box = self.driver.find_element_by_css_selector(
                            '.pluggable-input-body.copyable-text.selectable-text')
                        msg_box.click()
                        break
                    except Exception as exp:
                        time.sleep(1)
                self.search_bar = self.driver.find_element_by_css_selector('.copyable-text.selectable-text')
                msg_box.clear()
                self.copy_paste_message(message.message.text)
                if app.config['SEND_MSG']:
                    msg_box = self.driver.find_element_by_css_selector(
                        '.pluggable-input-body.copyable-text.selectable-text')
                    msg_box.send_keys(Keys.ENTER)
                    message.sent_date = datetime.now()
                    message.status = 2
                    message.update()

    def message_broadcast(self, message_text, channels):
        for channel_name in channels:
            input_box = self.driver.find_element(By.XPATH, '//*[@id="side"]//input')
            input_box.clear()
            input_box.click()
            print(channel_name)
            input_box.send_keys(channel_name)
            chat_panel = self.driver.find_element_by_id('side')
            bs = BeautifulSoup(chat_panel.get_attribute('innerHTML'), "html.parser")
            time_spent = 0
            time.sleep(1)
            while not self.driver.find_elements_by_class_name('_3Burg'):
                print("loader..")
                time.sleep(1)
                time_spent += 1
                if time_spent > 60:
                    break
            if time_spent > 60:
                continue
            time.sleep(1)
            print(bs.find("div", {"class": CLASSES['chat_contact']}))
            if bs.find("div", {"class": CLASSES['chat_contact']}):
                try:
                    self.search_bar.send_keys(Keys.ENTER)
                    msg_box = self.driver.find_element_by_css_selector(
                        '.pluggable-input-body.copyable-text.selectable-text')
                    msg_box.click()
                    time.sleep(2)
                    msg_box.clear()
                    self.copy_paste_message(message_text)
                    time.sleep(2)
                    if app.config['SEND_MSG']:
                        msg_box.send_keys(Keys.ENTER)

                except Exception as e:
                    logging.exception(e)

    def send_messages(self):
        req = requests.get(URLS['get_channel'], params={'consumer_key': SENDERS_MAPPING[SENDER_ID]}).json()
        relations_channel_id = req['result'][0]['id']
        req = requests.get(URLS['get_message'], {'status': 1, 'channel_id': relations_channel_id}).json()
        messages = req['result']

        for message in messages:
            print(message)
            self.search_bar.clear()
            if message['user_account']['user']['phone']:
                self.search_bar.send_keys(message['user_account']['user']['phone'])
            else:
                self.search_bar.send_keys(message['user_account']['user']['name'])

            chat_panel = self.driver.find_element_by_css_selector('.chatlist-panel-body')
            bs = BeautifulSoup(chat_panel.get_attribute('innerHTML'), "html.parser")
            time_spent = 0
            while not self.driver.find_elements_by_class_name('_2xarx'):
                print("loader..")
                time.sleep(1)
                time_spent += 1
                if time_spent > 60:
                    break
            if time_spent > 60:
                continue
            time.sleep(1)
            if bs.find("div", {"class": "chat-drag-cover"}) or bs.find("div", {"class": "chat contact"}):
                print("chat found")
                try:
                    self.search_bar.send_keys(Keys.ENTER)
                    msg_box = self.driver.find_element_by_css_selector(
                        '.pluggable-input-body.copyable-text.selectable-text')
                    msg_box.click()
                    time.sleep(2)
                    msg_box.clear()
                    self.copy_paste_message(message['message'])
                    time.sleep(2)
                    if app.config['SEND_MSG']:
                        msg_box.send_keys(Keys.ENTER)
                        req = requests.put(URLS['post_message']+str(message['id']),
                                           json={'status': 2, 'sent_date': datetime.now(tdg_tz).timestamp()}).json()
                        print(req)
                        # message.sent_date = datetime.now()
                        # message.status = 2
                        # message.update()

                except Exception as e:
                    logging.exception(e)
            else:
                print("chat not found")

    def extract_unread_messages(self, group):
        self.search_bar.clear()
        self.search_bar.send_keys(group.name)
        time.sleep(2)
        chat_panel = self.driver.find_element_by_css_selector('.chatlist-panel-body')
        bs = BeautifulSoup(chat_panel.get_attribute('innerHTML'), "html.parser")
        if bs.find("div", {"class": "chat unread"}):
            self.search_bar.send_keys(Keys.ENTER)
            try:
                self.driver.find_element_by_css_selector(".incoming-msgs").click()
            except Exception as e:
                pass
                # logging.exception(e)
            try:
                chat_body = self.driver.find_element_by_css_selector('._9tCEa')
                soup = BeautifulSoup(chat_body.get_attribute('innerHTML'), "html.parser")
                # try:
                #     last_msg = soup.find_all("div", {"class": "bubble bubble-text has-author copyable-text"})[0]
                # except Exception:
                #     import traceback
                #     print(traceback.print_exc())
                # qry = Database.query.filter_by(channel=c.name).order_by('datetime').all()
                # if qry:
                #     try:self.search_bar.clear()
                #         tym = qry[-1].datetime.replace(tzinfo=None)
                #         t = get_timestamp(last_msg['data-pre-plain-text'].split(']')[0][1:])
                #         while t > tym:
                #             driver.execute_script(
                #                 'document.getElementsByClassName("pane-chat-body")[0].scrollTop = 0')
                #             time.sleep(3)
                #             soup = BeautifulSoup(chat_body.get_attribute('innerHTML'), "html.parser")
                #             m = soup.find_all("div", {"class": "bubble bubble-text has-author copyable-text"})[0]
                #             t = get_timestamp(m['data-pre-plain-text'].split(']')[0][1:])
                #     except Exception as e:
                msgs = soup.find_all("div", {"class": "bubble bubble-text has-author copyable-text"})
                for msg in msgs:
                    data_dict = extract_message_content(
                        msg.find("span",
                                 {"class": "emojitext selectable-text invisible-space copyable-text"}).text)
                    data_dict['text'] = msg.find("span", {
                        "class": "emojitext selectable-text invisible-space copyable-text"}).text
                    number_obj = msg.find("span", {'class': 'RZ7GO'})
                    channel = self.add_channel(number_obj, data_dict, msg)
                    if not channel:
                        continue
                    data_dict['sent_date'] = get_timestamp(msg['data-pre-plain-text'].split(']')[0][1:] + ' IST')

                    add_message_in_db(group, channel, data_dict, SENDER_ID)

            except Exception as e:
                logging.exception(e)
                import traceback
                logging.exception(traceback.print_exc())
                print(traceback.print_exc())

    def send_msgs(self, vendors, clients, channels):
        num = 1
        if vendors or clients:
            sent_msg = HEADER
            if vendors:
                sent_msg += "----- *AVAILABLE* -----\n"
            for v in vendors:
                if not v.altered_msg == "":
                    sent_msg += str(
                        num) + ". " + v.altered_msg.lower() + '\n' + '--------------------------------------------------' + '\n'
                    num += 1
                v.sent = True
                v.save()
            if clients:
                sent_msg += "----- *NEED* -----\n"
            for c in clients:
                if not c.altered_msg == "":
                    sent_msg += str(
                        num) + ". " + c.altered_msg.lower() + '\n' + '--------------------------------------------------' + '\n'
                    num += 1
                c.sent = True
                c.save()
            sent_msg += FOOTER
            o = Message({'sent_message': sent_msg})  # TODO changes this
            o.save()
            for x in vendors + clients:
                x.msg_id = o.id
                x.save()
            for c in channels:
                o.channel.append(c)
                o.save()
                self.search_bar.clear()
                time.sleep(2)
                self.search_bar.send_keys(c.name + Keys.ENTER)
                msg_box = self.driver.find_element_by_css_selector(
                    '.pluggable-input-body.copyable-text.selectable-text')
                msg_box.click()
                try:
                    msg_box.clear()
                    self.copy_paste_message(sent_msg)

                    if app.config['SEND_MSG']:
                        msg_box.send_keys(Keys.ENTER)
                except Exception as e:
                    logging.exception(e)

    def extract_group_contacts(self, group):
        self.search_bar.clear()
        self.search_bar.send_keys(group.name)
        time.sleep(10)
        chat_panel = self.driver.find_element_by_css_selector('.chatlist-panel-body')
        bs = BeautifulSoup(chat_panel.get_attribute('innerHTML'), "html.parser")
        if bs.find("div", {"class": "chat"}):
            self.search_bar.send_keys(Keys.ENTER)
            try:
                self.driver.find_element_by_css_selector('.pane-chat-header').click()
                time.sleep(5)
                print("time")
                contact_body = self.driver.find_element_by_css_selector('._2sNbV')
                soup = BeautifulSoup(contact_body.get_attribute('innerHTML'), "html.parser")
                participants = None
                while not participants:
                    participants = soup.find("div", {"class": "_1CRb5 _34vig", 'data-list-scroll-offset': 'true'})
                    time.sleep(2)
                print(participants.find("div", {"class": "_1ZiJ3"}).text)
                contact_len = int(participants.find("div", {"class": "_1ZiJ3"}).text.split('of')[0])
                self.driver.execute_script("document.getElementsByClassName('_2sNbV')[0].scrollBy(0,500);")
                while contact_len > 0:
                    soup = BeautifulSoup(contact_body.get_attribute('innerHTML'), "html.parser")
                    contact_list = soup.findAll("div", {"class": "_2wP_Y"})

                    for contact in contact_list:
                        sender_obj = contact.find("span", {'class': 'emojitext screen-name-text'})
                        number = contact.find("span", {'class': 'emojitext ellipsify'}).text
                        if not get_number(number):
                            continue
                        ph = extract_phone(number)
                        channel = Channel.query.filter_by(number=ph['number']).first()
                        if not channel:
                            if sender_obj and sender_obj.text:
                                sender_name = sender_obj.text
                            else:
                                sender_name = None
                            channel_obj = {
                                'number': ph['number'],
                                'isd_code': ph['isd_code'],
                                'name': sender_name,
                                'group': False,
                                'alternate_numbers': None,
                                'website': None,
                                'email': None,
                                'sender_id': SENDER_ID
                            }
                            add_channel_in_db(channel_obj)
                    self.driver.execute_script("document.getElementsByClassName('_2sNbV')[0].scrollBy(0,720);")
                    contact_len -= 10

            except Exception as exp:
                print(exp)

    def extract_complete_group(self, group):
        self.search_bar.clear()
        self.search_bar.send_keys(group.name)
        time.sleep(10)
        chat_panel = self.driver.find_element_by_css_selector('.chatlist-panel-body')
        bs = BeautifulSoup(chat_panel.get_attribute('innerHTML'), "html.parser")
        if bs.find("div", {"class": "chat"}):
            self.search_bar.send_keys(Keys.ENTER)
            try:
                chat_end = False
                while not chat_end:
                    contact_body = self.driver.find_element_by_css_selector('.pane-chat-body')
                    soup = BeautifulSoup(contact_body.get_attribute('innerHTML'), "html.parser")
                    chat_end = soup.find("div", {"class": "message-e2e_notification"})
                    time.sleep(1)
                    self.driver.execute_script("document.getElementsByClassName('pane-chat-body')[0].scrollBy(0,-10000);")
                print("time")
                chat_body = self.driver.find_element_by_css_selector('._9tCEa')
                soup = BeautifulSoup(chat_body.get_attribute('innerHTML'), "html.parser")
                msgs = soup.find_all("div", {"class": "bubble bubble-text has-author copyable-text"})
                for msg in msgs:
                    try:
                        data_dict = extract_message_content(
                            msg.find("span",
                                     {"class": "emojitext selectable-text invisible-space copyable-text"}).text)
                        data_dict['text'] = msg.find("span", {
                            "class": "emojitext selectable-text invisible-space copyable-text"}).text
                        number_obj = msg.find("span", {'class': 'RZ7GO'})
                        channel = self.add_channel(number_obj, data_dict, msg)
                        if not channel:
                            continue
                        data_dict['sent_date'] = get_timestamp(msg['data-pre-plain-text'].split(']')[0][1:] + ' IST')
                        add_message_in_db(group, channel, data_dict, SENDER_ID)

                    except Exception as exp:
                        print(exp)

                group.last_crawled = datetime.now(tdg_tz)
                group.save()
                # self.driver.find_element_by_xpath('//div[@class="pane-chat-controls"]/div/div/div/span[@data-icon="menu"]').click()
                self.driver.execute_script("""var event = new MouseEvent('mousedown', {
                        view: window,
                        bubbles: true,
                        cancelable: false
                      });
                    el = document.querySelector('header.pane-header.pane-chat-header').querySelector('span[data-icon="menu"]');
                    el.dispatchEvent(event)""")
                # self.driver.find_elements_by_css_selector('.pane-body.pane-chat-tile-container').click()
                time.sleep(2)
                self.driver.find_elements_by_css_selector('._10anr.vidHz._28zBA')[3].click()
                time.sleep(2)
                self.driver.find_element_by_css_selector('._1WZqU.PNlAR').click()

            except Exception as exp:
                print(exp)

    def map_channel(self):
        channels_to_map = []
        try:
            channels = Channel.query.filter(Channel.sender_id == None, blacllist=False).all()
            print(channels)
            for channel in channels:
                self.search_bar.clear()
                if channel.group:
                    self.search_bar.send_keys(channel.name)
                else:
                    self.search_bar.send_keys(channel.number)
                time.sleep(2)
                chat_panel = self.driver.find_element_by_css_selector('.chatlist-panel-body')
                bs = BeautifulSoup(chat_panel.get_attribute('innerHTML'), "html.parser")
                if bs.find("div", {"class": "chat-drag-cover"}):
                    print(channel)
                    channels_to_map.append(channel)
            print("total groups", len(channels_to_map))
            self.map_sender(channels_to_map)

            return channels_to_map
        except Exception as e:
            logging.exception(e)

    def get_channels_bytype(self, channel_type='group'):
        channels = []
        try:
            for i in range(1, 200):
                chat_list = self.driver.find_element_by_css_selector('.chatlist-panel-body')
                soup = BeautifulSoup(chat_list.get_attribute('innerHTML'), "html.parser")
                chats = soup.find_all("div", {"class": "chat"})
                for c in chats:
                    if c.find("span", {"data-icon": "default-"+channel_type}):
                        name = c.find("div", {"class": "chat-title"}).text
                        channels.append(name)
                self.driver.execute_script("document.getElementById('pane-side').scrollBy(0,720)")
            print("total channels", len(channels))
            return channels
        except Exception as e:
            logging.exception(e)

    def send_message_noncontacts(self, phone, message):
        self.driver.get("https://web.whatsapp.com/send?phone={phone}".
                        format(phone=phone, message=message))
        time.sleep(5)

    def map_sender(self, channels):
        for c in channels:
            if not c.sender_id:
                c.sender_id = app.config['SENDER_ID']
                c.save()

    def add_group_channels(self, channels):
        for channel_name in channels:
            channel_obj = {
                'name': channel_name,
                'group': True,
                'alternate_numbers': None,
                'sender_id': SENDER_ID
            }
            channel = Channel.query.filter_by(name=channel_name).first()
            if not channel:
                Channel(**channel_obj).save()
            print(channel_obj)

    def add_channel(self, number_obj, data_dict, msg):
        if number_obj:
            ph = extract_phone(number_obj.text)
            channel = Channel.query.filter_by(number=ph['number']).first()
            if not channel:
                sender_obj = msg.find("span", {'class': 'emoji-text-clickable'})
                if sender_obj and sender_obj.text:
                    sender_name = sender_obj.text
                else:
                    sender_name = None

                channel_obj = {
                    'number': ph['number'],
                    'isd_code': ph['isd_code'],
                    'name': sender_name,
                    'group': False,
                    'alternate_numbers': data_dict['number'],
                    'website': data_dict['website'],
                    'email': data_dict['email'],
                    'sender_id': SENDER_ID
                }
                channel = add_channel_in_db(channel_obj)
            else:
                if not channel.website and data_dict['website']:
                    channel.website = data_dict['website']
                    channel.save()
                if not channel.email and data_dict['email']:
                    channel.email = data_dict['email']
                    channel.save()
        else:
            sender_name = "".join(msg.findChildren()[1].text.split(" "))
            channel = Channel.query.filter_by(name=sender_name).first()
        if data_dict['group_link']:
            if not Group.query.filter_by(link=data_dict['group_link']).all():
                Group(link=data_dict['group_link'], channel_id=channel.id).save()

        return channel

    def get_mapped_channels(self):
        yesterday_date = datetime.now(tdg_tz) - timedelta(hours=24)
        channels = Channel.query.filter(Channel.sender_id == SENDER_ID,
                                        or_(Channel.blacklist == False,
                                            Channel.blacklist != None),
                                        or_(Channel.last_crawled <= yesterday_date,
                                            Channel.last_crawled == None),
                                        Channel.group == True).all()
        # channels = Channel.query.filter(Channel.name.in_([
        #     "Holiday Deals only", "IATA Accredited Agent 5", "KOLKATA Tour Agents Only", "GOA B2B - AMIR HOLIDAYS",
        #     "B2B Domestic & Outbound", "Buraq Holidays chikmglr2","KERALA B2B_ AMIR HOLIDAYS", "Holiday Queries",
        #     "Travel agents (B2B) ", "Tours & Travels (Agents)", "Holiday packages india ",
        #     "IATA Accredited Agent 3", "South India Tours B2B", "V Resorts-Best B2B Rates", "B2B",
        #     "Tours&Travels b2b s", "B2B TRAVEL AGENTS", "Travel Agents 1@ Orion", "WE PROVIDE B2B PACKAGES",
        #     "TaxieTourAgents B2bClub1", "holidays @Kerala", "Goa holiday", "HOLIDAY DESTINY  ",
        #     "Sikkim SilkRout Tour B2B", "JMAA TOUR & TRAVELS B2B", "B2B hotel queries",
        #     "In/out Bound Travel Agent", "B2B Friends Tourism Boss", "Hotels for Travel Agent",
        #     "Delhi Travel Agent", "Holidaybazaar posts only", "IATA Accredited Agent",
        #     "ANDAMAN B2B AMIR HOLIDAYS", "Only Gujarat Agent", "AWESOME HOLIDAY RAJASTHAN",
        #     "Mygoto B2B Tour & Travel", "Only Travel Agent", "Buraq holidays chikmglr",
        #     "Indian - Travel Agents", "COORG B2B - AMIR HOLIDAYS", "Only B2B Travel Queries",
        #     "Travel Agent India B2B", "BLR Titanz B2b Xpress", "China/Hongkong/Macau B2B",
        #     "TaxieTour AgentsB2Bclub2", "B2B Dubai Green Point", "Join Hands agents",
        #     "B2B Travel Leads Bidding!", "Dubai 3 B2B Deals & Offer", "B2B worldwide hotel rate",
        #     "B2B South Indian Tour", "Travel agents only"]),
        #     or_(Channel.last_crawled <= yesterday_date,
        #         Channel.last_crawled == None)).all()

        return channels

    def copy_paste_message(self, message):
        pyperclip.copy(message)
        if platform.system() == 'Darwin':
            ActionChains(self.driver).key_down(Keys.COMMAND).send_keys("v").key_up(
                Keys.COMMAND).perform()
        else:
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("v").key_up(
                Keys.CONTROL).perform()
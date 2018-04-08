# -*- coding: utf-8 -*-
__author__ = 'himanshujain.2792'

import re
from datetime import datetime


''' A line can be either:
        09/12/2012 17:03:48: Sender Name: Message
        3/24/14, 1:59:59 PM: Sender Name: Message
        24/3/14, 13:59:59: Sender Name: Message
'''


class ParserWhatsapp():

    def __init__(self, raw_messages):
        self.raw_messages = raw_messages

    def parse(self):
        messages = []

        for line in self.raw_messages:
            # Strip line
            # line = line.strip()

            # Skip empty lines
            # if line in ["", "\n", "\r\n", "\r"]:
            #     continue

            try:
                # Remove timestamp
                if not re.search("\d{1,2}\/\d{1,2}\/\d{1,2}, \d{1,2}:\d{1,2} \w{1,2} - ", line):
                    raise
                msg_date, sep, msg = line.partition(" - ")
                raw_date, sep, time = msg_date.partition(" ")
                sender, sep, content = msg.partition(": ")
                raw_date = raw_date.replace(",", "")
                year = raw_date.split(" ")[0].split("/")[-1]
                # The following lines treats:
                # 3/24/14 1:59:59 PM
                # 24/3/14 13:59:59 PM
                # Couldn't we use msg_date instead of chatTimeString here?

                # colonIndex = [x.start() for x in re.finditer(':', l)]
                # print l, colonIndex
                # chatTimeString = l[0:colonIndex[2]]
                # This ignores a minority of bad formatted lines using try/except block.
                # an execption is raised when the datetime_obj is not created due to date parsing error
                try:
                    if "AM" in msg_date or "PM" in msg_date:
                        datetime_obj = datetime.strptime(
                            msg_date, "%m/%d/%y, %I:%M %p")
                    else:
                        if len(year) == 2:
                            datetime_obj = datetime.strptime(msg_date, "%m/%d/%y %H:%M:%S")
                        else:
                            datetime_obj = datetime.strptime(msg_date, "%m/%d/%Y %H:%M:%S")
                except ValueError as exp:
                    print(exp)
                    continue

                line = re.sub("\d{1,2}\/\d{1,2}\/\d{1,2}, \d{1,2}:\d{1,2} \w{1,2} - ", "", line)

                # Remove and store date
                # date, line = line.split(" ", 1)

                # Remove and store sender
                sender, line = line.split(": ", 1)
                sender = sender.replace('\u202a', '').replace('\u202c', '').strip()

                messages.append({'sent_date': datetime_obj,
                                 'sender': sender,
                                 'message': line})
            except Exception as exp:

                if line != 'Messages to this chat and calls are now secured with end-to-end encryption.' \
                           ' Tap for more info.' and messages:
                    messages[len(messages)-1]['message'] += line

        return messages
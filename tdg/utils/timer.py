# -*- coding: utf-8 -*-
import time
import datetime
from dateutil.parser import parse, tz


def get_timestamp(time_string):
    return parse(time_string).astimezone(tz.tzlocal())
    # datetime.datet(int(time.mktime(time.strptime(time_string, '%H:%M, %m/%d/%Y'))) - time.timezone)


def get_datetime(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%c')


def get_epoch(date):
    # for i in data:
    #     i['datetime'] = i['datetime'].strftime('%s')
    return int(date.strftime('%s'))


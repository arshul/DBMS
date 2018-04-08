# -*- coding: utf-8 -*-tdg
__author__ = 'himanshujain.2792'

import time


def safe_execute(default, exception, *args):
    try:
        return int(time.mktime(time.strptime(str(*args)[:19], "%Y-%m-%d %H:%M:%S"))) - time.timezone
    except exception:
        return default
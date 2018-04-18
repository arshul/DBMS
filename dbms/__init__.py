# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from pytz import timezone
app = Flask(__name__)
app.config.from_pyfile('../config.cfg')
db = SQLAlchemy(app)
ma = Marshmallow(app)
tdg_tz = timezone(app.config.get('SERVER_TIMEZONE', 'Etc/UTC'))

# import .views.groups


##############
#   LOGGER   #
##############


def make_logger():
    from logging.config import dictConfig
    import logging
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'verbose': {
                'format': '[%(asctime)s] %(levelname)s [module - %(module)s process - %(process)d  thread - %('
                          'thread)d [ '
                          '%(name)s: %(funcName)s: %(pathname)s: %(lineno)s] %(message)s '
            },
            'simple': {
                'format': '%(levelname)s:%(message)s'
            },
            'email': {
                'format': 'Timestamp: %(asctime)s\nModule: %(module)s\n Line: %(lineno)d\nMessage: %(message)s'
            },
        },

        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'verbose',
                'filename': 'conveyor.log',
                'mode': 'a',
                'maxBytes': 50 * 1024 * 1024,
                'backupCount': 10,
            }
        },

        'loggers': {
            'extensive': {
                'level': 'DEBUG',
                'handlers': ['file', ]
            },
        }
    })

    return logging.getLogger('extensive')


# Initialize logger
logging = make_logger()

from dbms.model import model
import dbms.views
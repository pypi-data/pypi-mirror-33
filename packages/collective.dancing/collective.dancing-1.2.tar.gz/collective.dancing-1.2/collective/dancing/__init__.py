import zope.i18nmessageid
MessageFactory = zope.i18nmessageid.MessageFactory('collective.dancing')

import logging
logger = logging.getLogger('collective.dancing')


def initialize(context):
    pass
#path is now done with collective.monkeypatcher

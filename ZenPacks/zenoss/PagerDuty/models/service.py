##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from . import enum
import serialization
import json

class Service(object):
    """A single PagerDuty service"""
    def __init__(self, name, id, service_key, type):
        self.name = name
        self.id = id
        self.service_key = service_key
        self.type = type

    def __repr__(self):
        return "Service(name='%s', id='%s', service_key='%s', type='%s')" % (self.name, self.id, self.service_key, self.type)

    def __json__(self):
        return json.dumps(self, cls=serialization.JSONEncoder)

    Type = enum(GenericEmail  = 'generic_email',
                GenericAPI    = 'generic_events_api',
                CloudKick     = 'Cloudkick',
                Keynote       = 'Keynote',
                Nagios        = 'Nagios',
                Pingdom       = 'Pingdom',
                ServerDensity = 'Server Density',
                SQLMonitor    = 'SQL Monitor')

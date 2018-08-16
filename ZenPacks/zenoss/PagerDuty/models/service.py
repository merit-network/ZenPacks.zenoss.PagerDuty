##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import json

class Service(object):
    """A single PagerDuty service"""
    def __init__(self, name, id, serviceKey, type):
        self.name = name
        self.id = id
        self.serviceKey = serviceKey
        self.type = type

    def __repr__(self):
        return "Service(name='%s', id='%s', serviceKey='%s', type='%s')" % (self.name, self.id, self.serviceKey, self.type)

    def __json__(self):
        return json.dumps(self, cls=ServiceJSONEncoder)


class ServiceJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Service):
            return super(ServiceJSONEncoder, self).default(obj)
        return obj.__dict__

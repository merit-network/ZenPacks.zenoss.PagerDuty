##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import json

from Globals import Persistent

class Account(Persistent):
    """
    A PagerDuty account consists of a subdomain and API access key.
    """
    def __init__(self, subdomain, apiAccessKey):
        self.subdomain = subdomain
        self.apiAccessKey = apiAccessKey

    def fqdn(self):
        return "%s.pagerduty.com" % self.subdomain

    def __json__(self):
        return json.dumps(self, cls=AccountJSONEncoder)

class AccountJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Account):
            return super(AccountJSONEncoder, self).default(obj)
        if obj._p_state == -1:
            # activate the ghost object manually
            obj._p_activate()
        return obj.__dict__

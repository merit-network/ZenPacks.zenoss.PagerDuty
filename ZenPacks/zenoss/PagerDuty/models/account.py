##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Globals import Persistent

class Account(Persistent):
    """
    A PagerDuty account consists of a subdomain and API access key.
    """
    def __init__(self, subdomain, apiAccessKey, apiTimeout=40):
        self.subdomain = subdomain
        self.apiAccessKey = apiAccessKey
        self.apiTimeout = apiTimeout

    def fqdn(self):
        return "%s.pagerduty.com" % self.subdomain

    def getDict(self):
        return {
            'subdomain': self.subdomain,
            'apiAccessKey': self.apiAccessKey,
            'apiTimeout': self.apiTimeout
        }
##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import json

from Products.Zuul.interfaces import IInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t

from Products.ZenModel.ZVersion import VERSION as ZENOSS_VERSION
from Products.ZenUtils.Version import Version

# Make the UI look good in Zenoss 3 and Zenoss 4
if Version.parse('Zenoss %s' % ZENOSS_VERSION) >= Version.parse('Zenoss 4'):
    SingleLineText = schema.TextLine
    MultiLineText = schema.Text
else:
    SingleLineText = schema.Text
    MultiLineText = schema.TextLine

def _serialize(details):
    return [{u'key':a, u'value':b} for a,b in zip(details.keys(), details.values())] 

class IPagerDutyEventsAPIActionContentInfo(IInfo):
    """
    Zope interface defining the names and types of the properties used by
    actions.PagerDutyEventsAPIAction.

    The "implementation" of this interface is defined in
    info.PagerDutyEventsAPIActionContentInfo.
    """

    serviceKey = SingleLineText(
        title       = _t(u'Service API Key'),
        description = _t(u'The API Key for the PagerDuty Service you want to alert.'),
        xtype       = 'pagerduty-api-events-service-list'
    )

    summary = SingleLineText(
        title       = _t(u'Description'),
        description = _t(u'The summary for the PagerDuty event.'),
        default     = u'${evt/summary}'
    )

    source = SingleLineText(
        title       = _t(u'Source'),
        description = _t(u'The unique location of the affected system, preferably a hostname or FQDN'),
        default     = u'${urls/eventUrl}',
    )

    details = schema.List(
        title       = _t(u'Details'),
        description = _t(u'Custom details to be sent.'),
        default     = [json.dumps(_serialize({
                    u'device':u'${evt/device}',
                    u'message':u'${evt/message}',
                    u'eventID':u'${evt/evid}',
                    }))],
        group       = _t(u'Details'),
        xtype='pagerduty-api-events-details-field')

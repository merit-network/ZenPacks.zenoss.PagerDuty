##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import Globals

from zope.component import adapts
from zope.interface import implements

from Products.ZenModel.NotificationSubscription import NotificationSubscription

from Products.Zuul.infos import InfoBase
from Products.Zuul.infos.actions import ActionFieldProperty

from interfaces import IPagerDutyEventsAPIActionContentInfo

class PagerDutyEventsAPIActionContentInfo(InfoBase):
    """
    Provides the "implementation" for IPagerDutyEventsAPIActionContentInfo.

    Based on the definitions for the builtin actions in Products.Zuul.infos.actions.
    """
    implements(IPagerDutyEventsAPIActionContentInfo)
    adapts(NotificationSubscription)

    service_key = ActionFieldProperty(IPagerDutyEventsAPIActionContentInfo, 'service_key')
    summary = ActionFieldProperty(IPagerDutyEventsAPIActionContentInfo, 'summary')
    description = ActionFieldProperty(IPagerDutyEventsAPIActionContentInfo, 'description')
    incident_key = ActionFieldProperty(IPagerDutyEventsAPIActionContentInfo, 'incident_key')
    details = ActionFieldProperty(IPagerDutyEventsAPIActionContentInfo, 'details')
##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

EVENT_API_URI = 'https://events.pagerduty.com/v2/enqueue'
ALL_PROPERTIES = ['serviceKey', 'summary', 'description', 'incidentKey', 'details']

from models import enum

EventType = enum(TRIGGER='trigger', ACKNOWLEDGE='acknowledge', RESOLVE='resolve')
Properties = enum(SERVICE_KEY='serviceKey', SUMMARY='summary', DESCRIPTION='description',
                  INCIDENT_KEY='incidentKey', DETAILS='details')

REQUIRED_PROPERTIES = [Properties.SERVICE_KEY, Properties.SUMMARY, Properties.DESCRIPTION, Properties.INCIDENT_KEY]

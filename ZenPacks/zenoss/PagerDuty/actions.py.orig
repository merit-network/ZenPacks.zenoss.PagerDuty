##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import json
import urllib2

import logging
log = logging.getLogger("zen.pagerduty.actions")

import Globals

from zope.interface import implements, providedBy
from zenoss.protocols.protobufs.zep_pb2 import STATUS_ACKNOWLEDGED

from Products.ZenModel.UserSettings import GroupSettings
from Products.ZenUtils.guid.guid import GUIDManager
from Products.ZenUtils.ProcessQueue import ProcessQueue

from Products.ZenModel.interfaces import IAction
from Products.ZenModel.actions import IActionBase, TargetableAction, ActionExecutionException
from Products.ZenModel.actions import processTalSource, _signalToContextDict
from Products.ZenModel.ZVersion import VERSION as ZENOSS_VERSION

from ZenPacks.zenoss.PagerDuty.interfaces import IPagerDutyEventsAPIActionContentInfo
from ZenPacks.zenoss.PagerDuty.constants import EVENT_API_URI, EventType, enum
from ZenPacks.zenoss.PagerDuty import version as zenpack_version

NotificationProperties = enum(SERVICE_KEY='service_key', SUMMARY='summary', DESCRIPTION='description',
                              INCIDENT_KEY='incident_key', DETAILS='details')

REQUIRED_PROPERTIES = [NotificationProperties.SERVICE_KEY, NotificationProperties.SUMMARY,
                       NotificationProperties.DESCRIPTION, NotificationProperties.INCIDENT_KEY]

API_TIMEOUT_SECONDS = 40

class PagerDutyEventsAPIAction(IActionBase):
    """
    Derived class to contact PagerDuty's events API when a notification is
    triggered.
    """
    implements(IAction)

    id = 'pagerduty'
    name = 'PagerDuty'
    actionContentInfo = IPagerDutyEventsAPIActionContentInfo

    shouldExecuteInBatch = False

    def __init__(self):
        super(PagerDutyEventsAPIAction, self).__init__()

    def setupAction(self, dmd):
        self.guidManager = GUIDManager(dmd)
        self.dmd = dmd

    def execute(self, notification, signal):
        """
        Sets up the execution environment and POSTs to PagerDuty's Event API.
        """
        log.debug('Executing Pagerduty Events API action: %s', self.name)
        self.setupAction(notification.dmd)

        if signal.clear:
            eventType = EventType.RESOLVE
        elif signal.event.status == STATUS_ACKNOWLEDGED:
            eventType = EventType.ACKNOWLEDGE
        else:
            eventType = EventType.TRIGGER

        # Set up the TALES environment
        environ = {'dmd': notification.dmd, 'env':None}

        actor = signal.event.occurrence[0].actor

        device = None
        if actor.element_uuid:
            device = self.guidManager.getObject(actor.element_uuid)
        environ.update({'dev': device})

        component = None
        if actor.element_sub_uuid:
            component = self.guidManager.getObject(actor.element_sub_uuid)
        environ.update({'component': component})

        data = _signalToContextDict(signal, self.options.get('zopeurl'), notification, self.guidManager)
        environ.update(data)

        try:
            details_list = json.loads(notification.content['details'])
        except ValueError:
            raise ActionExecutionException('Invalid JSON string in details')

        details = dict()
        for kv in details_list:
            details[kv['key']] = kv['value']

        details['zenoss'] = {
            'version'        : ZENOSS_VERSION,
            'zenpack_version': zenpack_version()
        }
        body = {'event_type': eventType,
                'client'    : 'Zenoss',
                'client_url': '${urls/eventUrl}',
                'details'   : details}

        for prop in REQUIRED_PROPERTIES:
            if prop in notification.content:
                body[prop] = notification.content[prop]
            else:
                raise ActionExecutionException("Required property '%s' not found" % (prop))

        self._performRequest(body, environ)

    def _performRequest(self, body, environ):
        """
        Actually performs the request to PagerDuty's Event API.

        Raises:
            ActionExecutionException: Some error occurred while contacting
            PagerDuty's Event API (e.g., API down, invalid service key).
        """
        request_body = json.dumps(self._processTalExpressions(body, environ))

        headers = {'Content-Type' : 'application/json'}
        req = urllib2.Request(EVENT_API_URI, request_body, headers)
        try:
            f = urllib2.urlopen(req, None, API_TIMEOUT_SECONDS)
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                msg = 'Failed to contact the PagerDuty server: %s' % (e.reason)
                raise ActionExecutionException(msg)
            elif hasattr(e, 'code'):
                msg = 'The PagerDuty server couldn\'t fulfill the request: HTTP %d (%s)' % (e.code, e.msg)
                raise ActionExecutionException(msg)
            else:
                raise ActionExecutionException('Unknown URLError occurred')

        response = f.read()
        f.close()

    def _processTalExpressions(self, data, environ):
        if type(data) is str or type(data) is unicode:
            if '${' not in data:
                return data
            try:
                return processTalSource(data, **environ)
            except Exception:
                raise ActionExecutionException(
                    'Unable to perform TALES evaluation on "%s" -- is there an unescaped $?' % data)
        elif type(data) is list:
            return [self._processTalExpressions(e, environ) for e in data]
        elif type(data) is dict:
            return dict([(k, self._processTalExpressions(v, environ)) for (k, v) in data.iteritems()])
        else:
            return data

    def updateContent(self, content=None, data=None):
        updates = dict()

        for k in NotificationProperties.ALL:
            updates[k] = data.get(k)

        content.update(updates)

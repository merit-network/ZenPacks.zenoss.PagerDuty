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
from requests import PagerDutyRequestLimitExceeded
from retry import retry

import logging
log = logging.getLogger("zen.pagerduty.actions")

from zope.interface import implements
from zenoss.protocols.protobufs.zep_pb2 import STATUS_ACKNOWLEDGED

from Products.ZenUtils.guid.guid import GUIDManager

from Products.ZenModel.interfaces import IAction
from Products.ZenModel.actions import IActionBase, ActionExecutionException
from Products.ZenModel.actions import processTalSource, _signalToContextDict
from Products.ZenModel.ZVersion import VERSION as ZENOSS_VERSION

from ZenPacks.zenoss.PagerDuty.routers import ACCOUNT_ATTR, _dmdRoot
from ZenPacks.zenoss.PagerDuty.interfaces import IPagerDutyEventsAPIActionContentInfo
from ZenPacks.zenoss.PagerDuty.constants import EVENT_API_URI, EventType, enum
from ZenPacks.zenoss.PagerDuty import version as zenpack_version

NotificationProperties = enum(SUMMARY='summary', SOURCE='source', SERVICE_KEY='serviceKey',
                              DETAILS='details')

REQUIRED_PROPERTIES = [NotificationProperties.SUMMARY, NotificationProperties.SOURCE]

EVENT_MAPPING = {'0': 'info', '1': 'info', '2': 'info',
                 '3': 'warning', '4': 'error', '5': 'critical'}


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

        if signal.clear:
            eventType = EventType.RESOLVE
        elif signal.event.status == STATUS_ACKNOWLEDGED:
            eventType = EventType.ACKNOWLEDGE
        else:
            eventType = EventType.TRIGGER

        log.debug('Executing Pagerduty Events API Action: %s', eventType)

        self.setupAction(notification.dmd)

        # Set up the TALES environment
        environ = {'dmd':notification.dmd, 'env':None}

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
            detailsList = json.loads(notification.content['details'])
        except ValueError:
            raise ActionExecutionException('Invalid JSON string in details')

        details = dict()
        for kv in detailsList:
            details[kv['key']] = kv['value']

        details['zenoss'] = {
            'version': ZENOSS_VERSION,
            'zenpack_version': zenpack_version(),
        }

        payload = {
            'severity': '${evt/severity}',
            'class': '${evt/eventClass}',
            'custom_details': details,
        }
        body = {'event_action': eventType,
                'dedup_key': data['evt'].evid,
                'payload': payload}

        for prop in REQUIRED_PROPERTIES:
            if prop in notification.content:
                payload.update({prop: notification.content[prop]})
            else:
                raise ActionExecutionException("Required property '%s' not found" % prop)

        log.debug('Pagerduty Request Body: %r', body)  # Log before adding API Key

        if NotificationProperties.SERVICE_KEY in notification.content:
            body.update({'routing_key': notification.content['serviceKey']})
        else:
            raise ActionExecutionException("API Key for PagerDuty service was not found. "
                                           "Did you configure a notification correctly?")

        self._performRequest(body, environ)

    @retry(exceptions=PagerDutyRequestLimitExceeded, delay=60, jitter=(1, 5))
    def _performRequest(self, body, environ):
        """
        Actually performs the request to PagerDuty's Event API.

        Raises:
            ActionExecutionException: Some error occurred while contacting
            PagerDuty's Event API (e.g., API down, invalid service key).
        """

        dmdRoot = _dmdRoot(self.dmd)
        apiTimeout = getattr(dmdRoot, ACCOUNT_ATTR).apiTimeout
        bodyWithProcessedTalesExpressions = self._processTalExpressions(body, environ)

        try:
            bodyWithProcessedTalesExpressions['payload']['severity'] = EVENT_MAPPING[bodyWithProcessedTalesExpressions['payload']['severity']]
        except KeyError:
            severity = bodyWithProcessedTalesExpressions['payload']['severity']
            if severity in EVENT_MAPPING.values():
                bodyWithProcessedTalesExpressions['payload']['severity'] = severity
        except Exception:
            raise

        requestBody = json.dumps(bodyWithProcessedTalesExpressions)

        headers = {'Content-Type': 'application/json'}
        req = urllib2.Request(EVENT_API_URI, requestBody, headers)
        try:
            # bypass default handler SVC-1819
            opener = urllib2.build_opener()
            f = opener.open(req, None, apiTimeout)
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                msg = 'Failed to contact the PagerDuty server: %s' % (e.reason)
                raise ActionExecutionException(msg)
            elif hasattr(e, 'code'):
                msg = 'The PagerDuty server couldn\'t fulfill the request: HTTP %d (%s)' % (e.code, e.msg)

                if e.code == 429:
                    raise PagerDutyRequestLimitExceeded(msg)
                else:
                    raise ActionExecutionException(msg)
            else:
                raise ActionExecutionException('Unknown URLError occurred')

        response = f.read()
        log.debug('PagerDuty response: %s', response)
        f.close()

    def _processTalExpression(self, value, environ):
        if type(value) is str or type(value) is unicode:
            if '${' not in value:
                return value
            try:
                return processTalSource(value, **environ)
            except Exception:
                raise ActionExecutionException(
                    'Unable to perform TALES evaluation on "%s" -- is there an unescaped $?' % value)
        else:
            return value

    def _processTalExpressions(self, data, environ):
        for payloadKey in data['payload']:
            if not payloadKey.startswith('custom_details'):
                data['payload'][payloadKey] = self._processTalExpression(data['payload'][payloadKey], environ)
        for detailKey in data['payload']['custom_details']:
            data['payload']['custom_details'][detailKey] = self._processTalExpression(data['payload']['custom_details'][detailKey], environ)
        return data

    def updateContent(self, content=None, data=None):
        updates = dict()

        for k in NotificationProperties.ALL:
            updates[k] = data.get(k)

        content.update(updates)

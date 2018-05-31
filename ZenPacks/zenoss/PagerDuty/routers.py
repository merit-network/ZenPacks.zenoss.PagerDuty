##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import requests
import models.account
import models.serialization

from Products.ZenUtils.Ext import DirectRouter, DirectResponse

import json
import logging
log = logging.getLogger('zen.PagerDuty.ServicesRouter')

ACCOUNT_ATTR = 'pagerduty_account'

def _dmdRoot(dmdContext):
    return dmdContext.getObjByPath("/zport/dmd/")

def _success(modelObj, msg=None):
    objData = json.loads(json.dumps(modelObj, cls=models.serialization.JSONEncoder))
    return DirectResponse.succeed(msg=msg, data=objData)

def _retrieveServices(account):
    log.info("Fetching list of PagerDuty services for %s..." % account.fqdn())
    try:
        apiServices = requests.retrieveServices(account)

    except requests.InvalidTokenException as e:
        log.warn("Token rejected")
        raise
    except requests.PagerDutyUnreachableException as e:
        log.warn("PagerDuty not reachable: %s" % e.message)
        raise
    except requests.ParseException as e:
        log.warn(e.message)
        raise

    log.info("Found %d services with integration of Events API V2  for %s" % (len(apiServices), account.fqdn()))
    return apiServices

class AccountRouter(DirectRouter):
    def __init__(self, context, request=None):
        super(AccountRouter, self).__init__(context, request)

    def getAccountSettings(self):
        """
        Retrieves the account object from /zport/dmd/pagerduty_account.
        """
        dmdRoot = _dmdRoot(self.context)
        account = getattr(dmdRoot, ACCOUNT_ATTR, models.account.Account(None, None))
        return _success(account)

    def updateAccountSettings(self, apiAccessKey=None, subdomain=None, wantsMessages=True):
        """
        Saves the account object and returns a list of services associated
        with that account.  Returns nothing if invalid account info is set.

        The account object is saved as /zport/dmd/pagerduty_account
        (aka, dmdRoot.pagerduty_account)
        """
        account = models.account.Account(subdomain, apiAccessKey)
        dmdRoot = _dmdRoot(self.context)
        setattr(dmdRoot, ACCOUNT_ATTR, account)

        if not account.apiAccessKey or not account.subdomain:
            return DirectResponse.succeed()

        servicesRouter = ServicesRouter(self.context, self.request)
        result = servicesRouter.get_services(wantsMessages)

        if result.data['success']:
            result.data['msg'] = "PagerDuty services retrieved successfully."
            apiServices = result.data['data']
            log.info("Successfully fetched %d PagerDuty generic API services.", len(apiServices))

        return result

class ServicesRouter(DirectRouter):
    """
    Simple router responsible for fetching the list of services from PagerDuty.
    """
    def getServices(self, wantsMessages=False):
        dmdRoot = _dmdRoot(self.context)
        noAccountMsg = 'PagerDuty account info not set.'
        setUpApiKeyInlineMsg = 'Set up your account info in "Advanced... PagerDuty Settings"'
        msg = noAccountMsg if wantsMessages else None
        if not hasattr(dmdRoot, ACCOUNT_ATTR):
            return DirectResponse.fail(msg=msg, inlineMessage=setUpApiKeyInlineMsg)

        account = getattr(dmdRoot, ACCOUNT_ATTR)
        if not account.apiAccessKey or not account.subdomain:
            return DirectResponse.fail(msg=msg, inline_message=setUpApiKeyInlineMsg)

        try:
            apiServices = _retrieveServices(account)
        except requests.InvalidTokenException:
            msg = 'Your api_access_key was denied.' if wantsMessages else None
            return DirectResponse.fail(msg=msg, inline_message='Access key denied: Go to "Advanced... PagerDuty Settings"')
        except requests.PagerDutyUnreachableException as pdue:
            msg = pdue.message if wantsMessages else None
            return DirectResponse.fail(msg=msg, inline_message=pdue.message)

        if not apiServices:
            msg = ("No services with events integration v2 were found for %s.pagerduty.com." % account.subdomain) if wantsMessages else None
            return DirectResponse.fail(msg=msg)
        
        return _success(apiServices)

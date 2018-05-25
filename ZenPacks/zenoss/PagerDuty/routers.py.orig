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
from models.service import Service
import models.serialization

from Products.ZenUtils.Ext import DirectRouter, DirectResponse

import json
import logging

log = logging.getLogger('zen.PagerDuty.ServicesRouter')

ACCOUNT_ATTR = 'pagerduty_account'


def _dmdRoot(dmdContext):
    return dmdContext.getObjByPath("/zport/dmd/")


def _success(model_obj, msg=None):
    obj_data = json.loads(json.dumps(model_obj, cls=models.serialization.JSONEncoder))
    return DirectResponse.succeed(msg=msg, data=obj_data)


def _retrieve_services(account):
    log.info("Fetching list of PagerDuty services for %s..." % account.fqdn())
    try:
        all_services = requests.retrieve_services(account)

    except requests.InvalidTokenException as e:
        log.warn("Token rejected")
        raise
    except requests.PagerDutyUnreachableException as e:
        log.warn("PagerDuty not reachable: %s" % e.message)
        raise
    except requests.ParseException as e:
        log.warn(e.message)
        raise

    api_services = [service for service in all_services if service.type == Service.Type.GenericAPI]
    log.info("Found %d services for %s" % (len(api_services), account.fqdn()))
    return api_services


class AccountRouter(DirectRouter):
    def __init__(self, context, request=None):
        super(AccountRouter, self).__init__(context, request)

    def get_account_settings(self):
        """
        Retrieves the account object from /zport/dmd/pagerduty_account.
        """
        dmdRoot = _dmdRoot(self.context)
        account = getattr(dmdRoot, ACCOUNT_ATTR, models.account.Account(None, None))
        return _success(account)

    def update_account_settings(self, api_access_key=None, subdomain=None, wants_messages=True):
        """
        Saves the account object and returns a list of services associated
        with that account.  Returns nothing if invalid account info is set.

        The account object is saved as /zport/dmd/pagerduty_account
        (aka, dmdRoot.pagerduty_account)
        """
        account = models.account.Account(subdomain, api_access_key)
        dmdRoot = _dmdRoot(self.context)
        setattr(dmdRoot, ACCOUNT_ATTR, account)

        if not account.api_access_key or not account.subdomain:
            return DirectResponse.succeed()

        services_router = ServicesRouter(self.context, self.request)
        result = services_router.get_services(wants_messages)

        if result.data['success']:
            result.data['msg'] = "PagerDuty services retrieved successfully."
            api_services = result.data['data']
            log.info("Successfully fetched %d PagerDuty generic API services.", len(api_services))

        return result


class ServicesRouter(DirectRouter):
    """
    Simple router responsible for fetching the list of services from PagerDuty.
    """

    def get_services(self, wants_messages=False):
        dmdRoot = _dmdRoot(self.context)
        no_account_msg = 'PagerDuty account info not set.'
        set_up_api_key_inline_msg = 'Set up your account info in "Advanced... PagerDuty Settings"'
        msg = no_account_msg if wants_messages else None
        if not hasattr(dmdRoot, ACCOUNT_ATTR):
            return DirectResponse.fail(msg=msg, inline_message=set_up_api_key_inline_msg)

        account = getattr(dmdRoot, ACCOUNT_ATTR)
        if not account.api_access_key or not account.subdomain:
            return DirectResponse.fail(msg=msg, inline_message=set_up_api_key_inline_msg)

        try:
            api_services = _retrieve_services(account)
        except requests.InvalidTokenException:
            msg = 'Your api_access_key was denied.' if wants_messages else None
            return DirectResponse.fail(msg=msg,
                                       inline_message='Access key denied: Go to "Advanced... PagerDuty Settings"')
        except requests.PagerDutyUnreachableException as pdue:
            msg = pdue.message if wants_messages else None
            return DirectResponse.fail(msg=msg, inline_message=pdue.message)

        if not api_services:
            msg = (
            "No generic event services were found for %s.pagerduty.com." % account.subdomain) if wants_messages else None
            return DirectResponse.fail(msg=msg)

        return _success(api_services)

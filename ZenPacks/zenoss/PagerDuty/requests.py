#############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import json
import urllib
import urlparse
import urllib2

from types import DictType, ListType
from models.service import Service


class InvalidTokenException(Exception):
    pass


class PagerDutyUnreachableException(Exception):
    pass


class ParseException(Exception):
    pass


def _addDefaultHeaders(req):
    _DEFAULT_HEADERS = {'Content-Type': 'application/json'}
    for header, value in _DEFAULT_HEADERS.iteritems():
        req.add_header(header, value)


def _invokePagerdutyResourceApi(uri,
                                headers,
                                jsonRoot,
                                timeoutSeconds=None,
                                limit=None,
                                offset=None):
    """
    Calls the PagerDuty API at uri and paginates through all of the results.
    """
    params = {}
    if offset is not None:
        params.update({'offset': offset})

    if limit is not None:
        params.update({'limit': limit})

    uriParts = list(urlparse.urlparse(uri))
    uriParts[4] = '%s&%s' % (urllib.urlencode(params), uriParts[4])
    queryUri = urlparse.urlunparse(uriParts)

    req = urllib2.Request(queryUri)
    for header, value in headers.iteritems():
        req.add_header(header, value)
    _addDefaultHeaders(req)

    try:
        f = urllib2.urlopen(req, None, timeoutSeconds)
    except urllib2.URLError as e:
        if hasattr(e, 'code'):
            if e.code == 401:  # Unauthorized
                raise InvalidTokenException()
            else:
                msg = 'The PagerDuty server couldn\'t fulfill the request: HTTP %d (%s)' % (e.code, e.msg)
                raise PagerDutyUnreachableException(msg)
        elif hasattr(e, 'reason'):
            msg = 'Failed to contact the PagerDuty server: %s' % (e.reason)
            raise PagerDutyUnreachableException(msg)
        else:
            raise PagerDutyUnreachableException()

    responseData = f.read()
    f.close()

    try:
        response = json.loads(responseData)
    except ValueError as e:
        raise ParseException(e.message)

    if type(response) is not DictType:
        raise ParseException('Dictionary not returned')

    if jsonRoot not in response:
        raise ParseException("Missing '%s' key in API response" % jsonRoot)

    resource = response[jsonRoot]

    if type(resource) is not ListType:
        raise ParseException("'%s' is not a list" % jsonRoot)

    more = response.get('more')
    limit = response.get('limit')
    offset = response.get('offset')

    if (limit is None or offset is None):
        return resource

    if more:
        newOffset = offset + limit
        return resource + _invokePagerdutyResourceApi(uri, headers, jsonRoot, timeoutSeconds, limit, newOffset)
    else:
        return resource


def validateAndAddServiceModels(servicesFromResponse):
    services = []
    for svcDict in servicesFromResponse:
        if ('name' in svcDict
           and 'id' in svcDict
           and 'type' in svcDict
           and 'integrations' in svcDict
           and len(svcDict['integrations']) >= 1):
            integration = svcDict['integrations'][0]
            if 'integration_key' in integration:
                service = Service(name=svcDict['name'],
                                  id=svcDict['id'],
                                  serviceKey=integration['integration_key'],
                                  type=svcDict['type'])
                services.append(service)

    return services


def retrieveServices(account):
    """
    Fetches the list of all services for an Account from the PagerDuty API.

    Returns:
        A list of Service objects.
    """
    uri = "https://api.pagerduty.com/services?include%5B%5D=integrations"
    headers = {'Authorization': 'Token token=' + account.apiAccessKey,
               'Accept': 'application/vnd.pagerduty+json;version=2'}
    jsonRoot = 'services'
    timeoutSeconds = 10
    allServices = _invokePagerdutyResourceApi(uri, headers, jsonRoot, timeoutSeconds)

    services = validateAndAddServiceModels(allServices)
    return services

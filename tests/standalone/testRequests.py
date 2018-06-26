##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018 all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import unittest
from ZenPacks.zenoss.PagerDuty.requests import validateAndAddServiceModels

TEST_V2_SERVICE = {'integrations': [{
                       'integration_key': '25765e25330e4d54a4b0aa3e265d9da1',
                       'type': 'events_api_v2_inbound_integration',
                       'id': 'P0MPHSK'}],
                   'id': 'P7LSV6M',
                   'type': 'service',
                   'name': 'A v2 Service'}
TEST_V2_SERVICE_2 = {'integrations': [{
                         'integration_key': '7317fbf8be4449aea2005d7695a6c34f',
                         'type': 'events_api_v2_inbound_integration',
                         'id': 'POH9JX0'}],
                     'id': 'PVGPXO2',
                     'type': 'service',
                     'name': 'Another v2 Service'}

TEST_ZENOSS_5_SERVICE = {'integrations': [{
                             'integration_key': '01822f4a783c4b669a6b2ce7c25343f4',
                             'type': 'generic_events_api_inbound_integration',
                             'id': 'PKX40F6'}],
                         'id': 'PGB9ZS5',
                         'type': 'service',
                         'name': 'Zenoss 5 Service'}

INVALID_SERVICE = {}

THREE_SERVICES_WITH_ONE_ZENOSS_5 = [TEST_V2_SERVICE, TEST_V2_SERVICE_2, TEST_ZENOSS_5_SERVICE]
THREE_SERVICES_WITH_ONE_INVALID = [TEST_V2_SERVICE, TEST_ZENOSS_5_SERVICE, INVALID_SERVICE]

class TestRequests(unittest.TestCase):

    def testFilterAndValidateServicesReturnsAllServices(self):
        services = validateAndAddServiceModels(THREE_SERVICES_WITH_ONE_ZENOSS_5)
        self.assertEquals(3, len(services))

    def testFilterAndValidateServicesReturnsTwoServicesWhenOneIsInvalid(self):
        services = validateAndAddServiceModels(THREE_SERVICES_WITH_ONE_INVALID)
        self.assertEquals(2, len(services))

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018 all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import unittest
from mock import Mock
import Globals
from ZenPacks.zenoss.PagerDuty.action import PagerDutyEventsAPIAction

RETURNED_DEDUP_KEY = 'f3ea87a602db49ebb3fdb98ddd3f4385'
SUCCESSFUL_RESPONSE = '{"status":"success","message":"Event processed","dedup_key":"' + RETURNED_DEDUP_KEY + '"}'

class MockNotification:

    def __init__(self):
        self.content = {
            'url': WSDL_URL,
            'proxyUrl': None,
            'proxyUsername': None,
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD,
            'retries': RETRIES,
            'timeout': TIMEOUT
        }

class TestAction(unittest.TestCase):

    def test

    def testGetWsdlUrl(self):
        notification = MockNotification()
        cherwellAction = CherwellAction()
        self.assertEquals(WSDL_URL, cherwellAction.getWsdlUrl(notification))

    def testExtractFieldFromBusinessObjectXMLFindsRecId(self):
        cherwellAction = CherwellAction()
        actualRecId = cherwellAction._extractFieldFromBusinessObjectXML('RecID',TEST_XML_WITH_REC_ID)
        self.assertEquals(REC_ID, actualRecId)

    def testExtractFieldFromBusinessObjectXMLRaisesExceptionForMissingField(self):
        cherwellAction = CherwellAction()
        self.assertRaises(CherwellAPIException, cherwellAction._extractFieldFromBusinessObjectXML, 'NotAField',TEST_XML_WITH_REC_ID)


    def testIsRecIdReturnsTrueForRecId(self):
        self.assertTrue(CherwellAction.isRecId(REC_ID))

    def testIsRecIdReturnsFalseForPublicId(self):
        self.assertFalse(CherwellAction.isRecId(PUBLIC_ID))

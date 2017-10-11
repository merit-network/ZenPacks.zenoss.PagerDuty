##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import json
import logging

from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration

from ZenPacks.PagerDuty.APINotification.interfaces import _serialize


log = logging.getLogger("zen.migrate")


class UpdateNotificationContentFields(ZenPackMigration):
    """
    Delete unnecessary fields from notification content
    """
    version = Version(1, 2, 0)
    old_properties = ['severity', 'ipAddress']

    def migrate(self, pack):

        log.debug("Fetching all notifications")
        all_notifications = pack.dmd.NotificationSubscriptions.objectValues()

        updated_details = {}
        log.debug("Deleting unnecessary fields")
        for notification in all_notifications:
            if notification.action.startswith('pagerduty'):
                original_content = notification.content
                old_details = json.loads(notification.content['details'])
                for detail_item in old_details:
                    if detail_item['key'] not in self.old_properties:
                        updated_details.update({detail_item['key']: detail_item['value']})
                    else:
                        continue
                original_content['details'] = json.dumps(_serialize(updated_details))
                original_content['service_key'] = ''
                notification.content = original_content


UpdateNotificationContentFields()

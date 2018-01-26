##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging

from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration

from ZenPacks.zenoss.PagerDuty.routers import ACCOUNT_ATTR
from ZenPacks.zenoss.PagerDuty.models.account import Account

log = logging.getLogger("zen.migrate")


class UpdateAccount(ZenPackMigration):
    """
    Update Account to inherit from Persistent
    """
    version = Version(1, 1, 1)

    def migrate(self, pack):
        log.debug("Fetching Account object")
        dmdRoot = pack.zport.dmd
        old_account = getattr(dmdRoot, ACCOUNT_ATTR)
        new_account = Account(old_account.subdomain, old_account.api_access_key)
        log.debug("Setting updated Account object")
        setattr(dmdRoot, ACCOUNT_ATTR, new_account)


UpdateAccount()

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import json

class JSONEncoder(json.JSONEncoder):
     def default(self, obj):
         import account
         import service

         if not isinstance(obj, (account.Account, service.Service)):
             return super(JSONEncoder, self).default(obj)

         return obj.__dict__

# -*- coding: utf-8 -*-
# Copyright 2018 NS Solutions Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function, absolute_import, unicode_literals, with_statement

from kamonohashi.models.account.account_info import AccountInfoModel
from kamonohashi.models.account.login import LoginModel
from kamonohashi.rest_call._account_call import AccountCall
from kamonohashi.util._module_logger import get_logger
from kamonohashi.util._sdk_base import SdkBase


class Account(SdkBase):
    def __init__(self, server, token=None, user=None, password=None, tenant=None,
                 timeout=30, retry=5):
        """Set logger and user_info

        :param server:
        :param token:
        :param user:
        :param password:
        :param tenant:
        :param timeout:
        :param retry:
        """
        super(Account, self).__init__(server=server, token=token, user=user, password=password, tenant=tenant,
                                      timeout=timeout, retry=retry)
        self.logger = get_logger(__name__)
        self.account_call = AccountCall(self._user_info)

    def login(self, user_name, password, tenant_name):
        """get a token to access kqi

        :rtype: LoginModel
        """
        self.logger.info('login to {0}.'.format(tenant_name))
        result = self.account_call._login(user_name, password, tenant_name)
        self.logger.info('Done')
        return result

    def switch_tenant(self, tenant_id, expireDays):
        """get a token for another tenant used by current tenant token

        :rtype: LoginModel
        """
        self.logger.info('Switching tenant to {0}.'.format(tenant_id))
        result = self.account_call._switch_tenant(tenant_id, expireDays)
        self.logger.info('Done')
        return result

    def get(self):
        """get account info

        :rtype: AccountInfoModel
        """
        self.logger.info('Getting login user account info.')
        result = self.account_call._get()
        return result

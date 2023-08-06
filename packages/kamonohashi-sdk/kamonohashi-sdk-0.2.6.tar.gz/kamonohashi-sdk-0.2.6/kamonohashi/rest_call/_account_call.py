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

from __future__ import print_function, absolute_import, with_statement

from kamonohashi.models.account.account_info import AccountInfoModel
from kamonohashi.models.account.login import LoginModel
from kamonohashi.rest_call.util._kqi_http_client import KqiHttpClient
from kamonohashi.rest_call.util._parse_helper import parse_content
from kamonohashi.util._module_logger import get_logger


class AccountCall(object):
    def __init__(self, user_info):
        self.logger = get_logger(__name__)
        self.user_info = user_info
        self.http_client = KqiHttpClient(server=self.user_info.server, token=self.user_info.token,
                                         timeout=self.user_info.timeout, retry=self.user_info.retry)

    def _login(self, user_name, password, tenant_name):
        """ Sing In

        :type user_name: str
        :type password: str
        :type tenant_name: str
        :rtype: LoginModel
        """
        api = '/api/v1/account/login'
        data = {
            'userName': user_name,
            'password': password,
            'tenantName': tenant_name
        }
        response = self.http_client.api_post(api, data, True)
        result = LoginModel(parse_content(response.content))
        return result

    def _switch_tenant(self, tenant_name, expireDays):
        """ Sing In Another tenant

        :type tenant_name: str
        """
        api = '/api/v1/account/tenants/{0}/token'.format(tenant_name)
        if expireDays is not None:
            api = api + '?expireDays={}'.format(expireDays)
        response = self.http_client.api_put(api, None, True)
        #result = LoginModel(parse_content(response.content))
        return response.json()

    def _get(self):
        """ Get current login account information

        :return: { userName, tenants(dict) }
        :rtype: AccountInfoModel
        """
        api = '/api/v1/account'
        response = self.http_client.api_get(api)
        #result = AccountInfoModel(parse_content(response.content))
        return response.json()

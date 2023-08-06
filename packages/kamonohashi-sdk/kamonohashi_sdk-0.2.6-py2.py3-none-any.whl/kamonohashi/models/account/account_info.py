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

from kamonohashi.util._encoder import resolve_encode
import six

class AccountInfoModel(object):
    def __init__(self, result):
        self.__user_name = resolve_encode(result['userName'])
        self.__selected_tenant = resolve_encode(result['selectedTenant'])
        self.__selected_tenant_name = resolve_encode(result['selectedTenantName'])
        self.__tenants = self._encode_tenants(result['tenants'])

    @staticmethod
    def _encode_tenants(tenants):
        """
        adopt resolve_encode method to values of tenants dict
        """
        encoded_tenants = {}
        for k, v in six.iteritems(tenants):
            encoded_tenants[k] = resolve_encode(v)

        return encoded_tenants

    @property
    def user_name(self):
        return self.__user_name

    @property
    def selected_tenant(self):
        return self.__selected_tenant

    @property
    def selected_tenant_name(self):
        return self.__selected_tenant_name

    @property
    def tenants(self):
        return self.__tenants

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


class LoginModel(object):
    def __init__(self, result):
        self.__token = resolve_encode(result.get('token'))
        self.__user_name = resolve_encode(result['userName'])
        self.__tenant_name = resolve_encode(result['tenantName'])
        self.__expires_in = result['expiresIn']

    @property
    def token(self):
        return self.__token

    @property
    def user_name(self):
        return self.__user_name

    @property
    def tenant_name(self):
        return self.__tenant_name

    @property
    def expires_in(self):
        return self.__expires_in

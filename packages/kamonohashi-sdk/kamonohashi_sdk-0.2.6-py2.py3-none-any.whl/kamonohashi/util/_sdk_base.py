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
"""
Base class for each SDK core file.
"""

from __future__ import print_function, absolute_import, unicode_literals, with_statement

from kamonohashi.util._user_info import UserInfo


class SdkBase(object):
    def __init__(self, server, token, user, password, tenant, timeout, retry):
        """Set user_info"""
        self.__user_info = UserInfo(server=server, token=token, user=user, password=password, tenant=tenant,
                                    timeout=timeout, retry=retry)

    @property
    def _user_info(self):
        return self.__user_info

    @staticmethod
    def _generate_query(query):
        """generate search query for API"""
        if query is not None and query.find("=") == -1:
            return "query=" + query
        return query

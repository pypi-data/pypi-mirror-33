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
import sys

from kamonohashi.util._module_logger import get_logger


class UserInfo:
    def __init__(self, server, token=None, user=None, password=None, tenant=None,
                 retry=5, timeout=30, no_proxy=False):
        self.logger = get_logger(__name__)
        self.server = server
        self.timeout = timeout
        self.retry = retry

        # user info
        if token:
            self.token = token
        elif user and password and tenant:
            raise NotImplementedError()
        else:
            self.logger.error('Please set {token} or {user, password, tenant}')
            sys.exit(1)

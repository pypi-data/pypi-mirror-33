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
manage REST API
"""
from __future__ import print_function, absolute_import, unicode_literals, with_statement

import requests
import urllib3
from kamonohashi.util._module_logger import get_logger
from requests.adapters import HTTPAdapter
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util import Retry

urllib3.disable_warnings(InsecureRequestWarning)


class HttpClient(object):
    def __init__(self, timeout=60, retry=5):
        """Constructor

        Args:
            timeout (int): Receive timeout
        """
        # サブクラスで設定されていた場合は無視
        if (not hasattr(self, "logger")) or self.logger is None:
            self.logger = get_logger(__name__)

        # get from config file
        self.timeout = (5, timeout)

        # retry settings
        self.session = requests.session()
        retries = Retry(
            total=retry,
            backoff_factor=0,
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

        # ignore SSL cert verify
        self.session.verify = False
        # proxy setting
        self.session.trust_env = False

    def post(self, url, data, headers=None, auth=None):
        """Post method"""
        self.logger.info('Posting....')
        response = self.session.post(url=url,
                                     data=data,
                                     timeout=self.timeout,
                                     headers=headers,
                                     auth=auth)
        self.logger.info('Done post')
        return response

    def get(self, url, stream=False, headers=None, auth=None, params=None):
        """Get method"""
        self.logger.info('Getting...')
        response = self.session.get(url=url,
                                    timeout=self.timeout,
                                    headers=headers,
                                    stream=stream,
                                    params=params,
                                    auth=auth)
        self.logger.info('Done get')
        return response

    def delete(self, url, headers=None, auth=None):
        """Delete method"""
        self.logger.info('Deleting...')
        response = self.session.delete(url=url,
                                       timeout=self.timeout,
                                       headers=headers,
                                       auth=auth)
        self.logger.info('Done delete')
        return response

    def put(self, url, data, headers=None, auth=None):
        """Put method"""
        self.logger.info('Putting...')
        response = self.session.put(url=url,
                                    data=data,
                                    timeout=self.timeout,
                                    headers=headers,
                                    auth=auth)
        self.logger.info('Done put')
        return response

    def patch(self, url, data, headers=None, auth=None):
        """Patch method"""
        self.logger.info('Patching...')
        response = self.session.patch(url=url,
                                      data=data,
                                      headers=headers,
                                      auth=auth)
        self.logger.info('Done patch')
        return response

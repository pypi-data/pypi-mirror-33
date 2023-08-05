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

from kamonohashi.rest_call._container_call import ContainerCall
from kamonohashi.util._module_logger import get_logger
from kamonohashi.util._sdk_base import SdkBase


class Container(SdkBase):
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
        super(Container, self).__init__(server=server, token=token, user=user, password=password, tenant=tenant,
                                        timeout=timeout, retry=retry)
        self.logger = get_logger(__name__)
        self.container_call = ContainerCall(self._user_info)

    def get_images(self):
        """Get images

        :rtype List[str]
        """
        self.logger.info('Listing container images.')
        result = self.container_call._get_images()
        return result

    def get_tags(self, image):
        """Get tags

        :param image:
        :rtype list[str]
        """
        self.logger.info('Listing tags of container image {0}.'.format(image))
        result = self.container_call._get_tags(image)
        return result

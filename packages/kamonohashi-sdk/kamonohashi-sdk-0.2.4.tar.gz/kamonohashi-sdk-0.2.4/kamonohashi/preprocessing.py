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

from kamonohashi.rest_call._preprocessing_call import PreprocessingCall
from kamonohashi.util._module_logger import get_logger
from kamonohashi.util._sdk_base import SdkBase

class Preprocessing(SdkBase):
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
        super(Preprocessing, self).__init__(server=server, token=token, user=user, password=password, tenant=tenant,
                                      timeout=timeout, retry=retry)
        self.logger = get_logger(__name__)
        self.preprocessing_call = PreprocessingCall(self._user_info)

    def list(self, count, query=None):
        """Get preprocessing list filtered by query

        :param count: the maximum number of result
        :param query:
        :rtype: list[IndexModel]
        """
        self.logger.info('Listing preprocessing.')
        per_page = count if count else 30
        result = self.preprocessing_call._list(per_page, 1, self._generate_query(query))
        return result

    def get_total(self, query=None):
        """Get total

        :param query:
        :rtype: int
        :return: total
        """
        self.logger.info('Getting total number of preprocessing.')
        result = self.preprocessing_call._get_total(self._generate_query(query))
        return result

    def get(self, id):
        """Get preprocessing in detail

        :param id:
        :rtype: DetailsModel
        """
        self.logger.info('Getting preprocessing {0}.'.format(id))
        result = self.preprocessing_call._get(id)
        return result

    def get_as_json(self, id):
        """Get preprocessing in detail in json format

        :param id:
        :rtype: DetailModel
        """
        self.logger.info('Getting preprocessing {0} in json format.'.format(id))
        result = self.preprocessing_call._get_as_raw(id)
        return result

    def create(self, dic):
        """Create preprocessing from valid dictionary

        :param: dict dic:
        :rtype: IndexModel
        :return:
        """
        self.logger.info('Creating preprocessing.')
        result = self.preprocessing_call._create(dic)
        self.logger.info('Done')
        return result

    def update(self, id, dic):
        """Update preprocessing entries

        :param id:
        :param dict dic:
        :rtype: IndexModel
        """
        self.logger.info('Updating preprocessing')
        result = self.preprocessing_call._update(id, dic)
        self.logger.info('Done')
        return result

    def update_meta_info(self, id, name, memo):
        """Update preprocessing meta information

        :param id:
        :param name:
        :param memo:
        :rtype: IndexModel
        """
        self.logger.info('Updating preprocessing meta info')
        result = self.preprocessing_call._update_meta_info(id, name, memo)
        self.logger.info('Done')
        return result

    def delete(self, id):
        """Delete preprocessing

        :param id:
        """
        self.logger.info('Deleting data {0}.'.format(id))
        self.preprocessing_call._delete(id)
        self.logger.info('Done')

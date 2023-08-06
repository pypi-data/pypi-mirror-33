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

from kamonohashi.rest_call.util._kqi_http_client import KqiHttpClient
from kamonohashi.rest_call.util._parse_helper import parse_content
from kamonohashi.util._module_logger import get_logger

from kamonohashi.models.preprocessing.index import IndexModel
from kamonohashi.models.preprocessing.details import DetailsModel

class PreprocessingCall(object):
    def __init__(self, user_info):
        self.logger = get_logger(__name__)
        self.user_info = user_info
        self.http_client = KqiHttpClient(server=self.user_info.server, token=self.user_info.token,
                                         timeout=self.user_info.timeout, retry=self.user_info.retry)

    def _list(self, per_page, page, query=None):
        """Get preprocessing list filtered by query

        :param per_page:
        :param page:
        :param query:
        :rtype: list[IndexModel]
        """
        api = '/api/v1/preprocessings?perPage={0}&page={1}'.format(per_page, page)
        if query is not None:
            api = api + '&' + query
        response = self.http_client.api_get(api)
        result = [IndexModel(x) for x in parse_content(response.content)]
        return result

    def _get_total(self, query=None):
        """Get total count of all preprocessing in a current tenant

        :param query:
        :rtype: int
        """
        api = '/api/v1/preprocessings/total'
        if query is not None:
            api = api + '?' + query
        result = self.http_client.api_get(api)
        return parse_content(result.content)

    def _get(self, id):
        """Get {id} preprocessing

        :param id:
        :return: DetailsModel
        """
        api = '/api/v1/preprocessings/{0}'.format(id)
        response = self.http_client.api_get(api)
        result = DetailsModel(parse_content(response.content))
        return result

    def _get_as_raw(self, id):
        """Get {id} preprocessing

        :param id:
        :return: DetailsModel
        """
        api = '/api/v1/preprocessings/{0}'.format(id)
        response = self.http_client.api_get(api)
        return response.content

    def _create(self, dic):
        """Create new preprocessing

        :param dict dic:
        :rtype: IndexModel
        """
        api = '/api/v1/preprocessings'
        response = self.http_client.api_post(api, dic, True)
        result = IndexModel(parse_content(response.content))
        return result

    def _update(self, id, dic):
        """Edit preprocessing

        :param id:
        :param dict dic:
        :rtype: IndexModel
        """
        api = '/api/v1/preprocessings/{0}'.format(id)
        response = self.http_client.api_put(api, dic, True)
        result = IndexModel(parse_content(response.content))
        return result

    def _update_meta_info(self, id, name=None, memo=None):
        """Edit preprocessing

        :param id:
        :param name:
        :param memo:
        :rtype: IndexModel
        """
        api = '/api/v1/preprocessings/{0}'.format(id)
        data = {
            'name': name,
            'memo': memo
        }
        response = self.http_client.api_patch(api, data, True)
        result = IndexModel(parse_content(response.content))
        return result

    def _delete(self, id):
        """Delete preprocessing

        :param id:
        """
        api = '/api/v1/preprocessings/{0}'.format(id)
        self.http_client.api_delete(api)


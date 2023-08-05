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

from kamonohashi.rest_call.util._kqi_http_client import KqiHttpClient
from kamonohashi.rest_call.util._parse_helper import parse_content
from kamonohashi.util._module_logger import get_logger

from kamonohashi.rest_call.models.data._simple import SimpleModel
from kamonohashi.models.data.file_info import FileInfoModel
from kamonohashi.models.data.index import IndexModel
from kamonohashi.models.data.details import DetailsModel


class DataCall(object):
    def __init__(self, user_info):
        self.logger = get_logger(__name__)
        self.user_info = user_info
        self.http_client = KqiHttpClient(server=self.user_info.server, token=self.user_info.token,
                                         timeout=self.user_info.timeout, retry=self.user_info.retry)

    def _list_simple(self, query=None):
        """Get data list with simple format filtered by query

        :param query: Nullable search query
        :rtype: list[SimpleModel]
        """
        api = '/api/v1/data/simple'
        payload = {}
        if query is not None:
            payload = {'query': query}
        response = self.http_client.api_get(api, False, payload)
        result = [SimpleModel(x) for x in parse_content(response.content)]
        return result

    def _list(self, per_page, page, query=None):
        """Get data list filtered by query

        :param per_page:
        :param page:
        :param query:
        :rtype: list[IndexModel]
        """
        api = '/api/v1/data?perPage={0}&page={1}'.format(per_page, page)
        if query is not None:
            api = api + '&' + query
        response = self.http_client.api_get(api)
        result = [IndexModel(x) for x in parse_content(response.content)]
        return result

    def _get_total(self, query=None):
        """Get total count of whole data in a current tenant

        :param query:
        :rtype: int
        """
        api = '/api/v1/data/total'
        if query is not None:
            api = api + '?' + query
        result = self.http_client.api_get(api)
        return parse_content(result.content)

    def _get(self, id):
        """Get {id} data

        :param id:
        :rtype: DetailsModel
        """
        api = '/api/v1/data/{0}'.format(id)
        response = self.http_client.api_get(api)
        result = DetailsModel(parse_content(response.content))
        return result

    def _create(self, name, image_name, image_path,
                annotation_name=None, annotation_path=None,
                memo=None, tags=None):
        """Create new data

        :param name:
        :param image_name:
        :param image_path:
        :param memo:
        :param annotation_name:
        :param annotation_path:
        :param tags:
        :rtype: IndexModel
        """
        api = '/api/v1/data'
        data = {
            'name': name,
            'memo': memo,
            'imageFileName': image_name,
            'imageFileStoredPath': image_path,
            'annotationFileName': annotation_name,
            'annotationFileStoredPath': annotation_path,
            'tags': tags
        }
        response = self.http_client.api_post(api, data, True)
        result = IndexModel(parse_content(response.content))
        return result

    def _update(self, id, memo=None, tags=None):
        """Edit data

        :param memo:
        :rtype: IndexModel
        """
        api = '/api/v1/data/{0}'.format(id)
        data = {
            'memo': memo,
            'tags': tags
        }
        response = self.http_client.api_put(api, data, True)
        result = IndexModel(parse_content(response.content))
        return result

    def _delete(self, id):
        """Delete data

        :param id:
        """
        api = '/api/v1/data/{0}'.format(id)
        self.http_client.api_delete(api)

    def _list_files(self, id):
        """get data file list

        :param id: data id
        :rtype: list[FileInfoModel]
        """
        api = '/api/v1/data/{0}/files'.format(id)
        response = self.http_client.api_get(api)
        result = [FileInfoModel(x) for x in parse_content(response.content)]

        return result

    def _get_file_info(self, id, key):
        """get data file information

        :param id: data id
        :param key: dedicate 'Image' or 'Annotation'
        :rtype: FileInfoModel
        """
        api = '/api/v1/data/{0}/files/{1}'.format(id, key)
        response = self.http_client.api_get(api)
        result = FileInfoModel(parse_content(response.content))
        return result

    def _create_file_info(self, id, file_name, key, storage_path):
        """Register a file to existing data entry

        :param id:
        :param file_name:
        :param key: designate 'Image' or 'Annotation'
        :param storage_path: object storage file path
        :rtype: FileInfoModel
        :return: registered file info
        """
        api = '/api/v1/data/{0}/files'.format(id)
        data = {
            'key': key,
            'fileName': file_name,
            'storedPath': storage_path
        }
        response = self.http_client.api_post(api, data, True)
        result = FileInfoModel(parse_content(response.content))
        return result

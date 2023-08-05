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

import ntpath

from kamonohashi.exception import KqiError
from kamonohashi.rest_call.models.storage._upload_complete import UploadCompleteModel
from kamonohashi.rest_call.models.storage._upload_parameter import UploadParameterModel
from kamonohashi.rest_call.util._kqi_http_client import KqiHttpClient
from kamonohashi.rest_call.util._parse_helper import parse_content
from kamonohashi.util._module_logger import get_logger


class StorageCall(object):
    def __init__(self, user_info):
        self.logger = get_logger(__name__)
        self.user_info = user_info
        self.http_client = KqiHttpClient(server=self.user_info.server, token=self.user_info.token,
                                         timeout=self.user_info.timeout, retry=self.user_info.retry)

    def _get_upload_parameter(self, file_path, file_type, part_sum):
        """Get pre signed url is for direct upload to object storage

        :param file_path:
        :param file_type:
        :param part_sum:
        :rtype UploadParameterModel
        """
        payload = {
            'FileName': ntpath.basename(file_path),
            'Type': file_type,
            'PartSum': part_sum
        }
        response = self.http_client.api_get('/api/v1/upload/parameter', params=payload)
        return UploadParameterModel(parse_content(response.content))

    def _complete_multi_upload(self, complete_model):
        """Complete multi part upload

        :param complete_model:
        :rtype: UploadCompleteModel
        """
        if complete_model['PartETags'].__len__() == 0:
            self.logger.error('The file is 0kb')
            raise KqiError('The file is 0kb')
        response = self.http_client.api_post('/api/v1/upload/complete', data=complete_model, as_json=True)
        return UploadCompleteModel(parse_content(response.content))

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

from kamonohashi.models.downloaded_file import DownloadedFileModel


class DownloadedDataSetEntryModel(object):
    def __init__(self, type, key, data_id, downloaded_file):
        """
        :type type: str
        :type key: str
        :type data_id: str
        :type downloaded_file: DownloadedFileModel
        """
        self.__type = type
        self.__key = key
        self.__data_id = data_id
        self.__downloaded_file = downloaded_file

    @property
    def type(self):
        return self.__type

    @property
    def key(self):
        return self.__key

    @property
    def data_id(self):
        return self.__data_id

    @property
    def downloaded_file(self):
        return self.__downloaded_file


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

from kamonohashi.models.dataset.index import IndexModel
from kamonohashi.models.data.file_info import FileInfoModel


class EntryModel(object):
    def __init__(self, result):
        self.__type = result['type']
        self.__files = [FileInfoModel(x) for x in result['files']]

    @property
    def type(self):
        return self.__type

    @property
    def files(self):
        # type: () -> list[FileInfoModel]
        return self.__files


class DataFileModel(IndexModel):
    def __init__(self, result):
        super(DataFileModel, self).__init__(result)
        self.__entries = [EntryModel(x) for x in result['entries']]

    @property
    def entries(self):
        # type: () -> list[EntryModel]
        return self.__entries

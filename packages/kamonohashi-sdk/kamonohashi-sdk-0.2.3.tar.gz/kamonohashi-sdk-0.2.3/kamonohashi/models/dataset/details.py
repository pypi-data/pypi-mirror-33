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

from kamonohashi.util._encoder import resolve_encode

from kamonohashi.models.data.index import IndexModel as DataIndexModel
from kamonohashi.models.dataset.index import IndexModel


class EntryModel(object):
    def __init__(self, type, result):
        self.__type = type
        self.__files = [DataIndexModel(x) for x in result]

    @property
    def type(self):
        return self.__type

    @property
    def files(self):
        # type: () -> list[DataIndexModel]
        return self.__files


class DetailsModel(IndexModel):
    def __init__(self, result):
        super(DetailsModel, self).__init__(result)
        self.__created_by = resolve_encode(result['createdBy'])
        self.__created_at = resolve_encode(result['createdAt'])
        self.__entries = [EntryModel(x, result['entries'][x]) for x in result['entries']]

    @property
    def created_by(self):
        return self.__created_by

    @property
    def created_at(self):
        return self.__created_at

    @property
    def entries(self):
        # type: () -> list[EntryModel]
        return self.__entries

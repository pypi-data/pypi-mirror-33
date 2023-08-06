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

from kamonohashi.models.index_interface import IndexModelInterface


class FileInfoModel(IndexModelInterface):
    def __init__(self, result):
        self.__id = result['id']
        self.__file_id = result['fileId']
        self.__key = resolve_encode(result['key'])
        self.__url = resolve_encode(result['url'])
        self.__name = resolve_encode(result['fileName'])

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def url(self):
        return self.__url

    @property
    def file_id(self):
        return self.__file_id

    @property
    def key(self):
        return self.__key

    def to_array(self):
        # テーブルで表示する際はDataIdとURLはを含めない
        return [self.file_id, self.key, self.name]

    def get_header(self):
        # テーブルで表示する際はDataIdとURLはを含めない
        return ['file id', 'key', 'file name']

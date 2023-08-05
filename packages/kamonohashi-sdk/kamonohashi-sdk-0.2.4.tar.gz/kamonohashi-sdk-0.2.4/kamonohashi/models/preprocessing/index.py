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


class IndexModel(IndexModelInterface):
    def __init__(self, result):
        self._id = result['id']
        self._name = resolve_encode(result['name'])
        self._memo = resolve_encode(result['memo'])
        self._created_at = resolve_encode(result['createdAt'])

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def memo(self):
        return self._memo

    @property
    def created_at(self):
        return self._created_at

    def to_array(self):
        return [self.id, self.name, self.memo]

    def get_header(self):
        return ['id', 'name', 'memo']

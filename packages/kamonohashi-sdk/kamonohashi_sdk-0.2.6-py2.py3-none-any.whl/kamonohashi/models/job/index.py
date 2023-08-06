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

from kamonohashi.models.dataset.index import IndexModel as DatasetIndexModel
from kamonohashi.models.index_interface import IndexModelInterface
from kamonohashi.models.job.simple import SimpleModel
from kamonohashi.util._encoder import resolve_encode


class IndexModel(IndexModelInterface, SimpleModel):
    def __init__(self, result):
        super(IndexModel, self).__init__(result)
        self.__dataset = DatasetIndexModel(result['dataSet'])
        self.__created_at = resolve_encode(result['createdAt'])

    @property
    def created_at(self):
        return self.__created_at

    @property
    def dataset(self):
        return self.__dataset

    def get_header(self):
        return ['id', 'name', 'started at', 'dataset', 'memo', 'status']

    def to_array(self):
        return [self.id, self.name, self.created_at, self.dataset.name, self.memo, self.status]

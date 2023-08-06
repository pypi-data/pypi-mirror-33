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

from kamonohashi.models.preprocessing.index import IndexModel
from kamonohashi.models.preprocessing.git_model import GitModelModel
from kamonohashi.models.preprocessing.container_image import ContainerImageModel

class DetailsModel:
    def __init__(self, result):
        git_model = result['gitModel']
        self._git_model = None if git_model is None else GitModelModel(git_model)
        container_image = result['containerImage']
        self._container_image = None if container_image is None else ContainerImageModel(container_image)
        self._index = IndexModel(result)
        self._entry_point = resolve_encode(result['entryPoint'])
        self._is_executed = result['isExecuted']

    @property
    def git_model(self):
        return self._git_model

    @property
    def container_image(self):
        return self._container_image

    @property
    def id(self):
        return self._index.id

    @property
    def name(self):
        return self._index.name

    @property
    def memo(self):
        return self._index.memo

    @property
    def created_at(self):
        return self._index.created_at

    @property
    def entry_point(self):
        return self._entry_point

    @property
    def is_executed(self):
        return self._is_executed


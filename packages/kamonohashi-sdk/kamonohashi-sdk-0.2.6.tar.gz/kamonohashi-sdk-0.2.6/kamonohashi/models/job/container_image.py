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

class ContainerImageModel:
    def __init__(self, result):
        self._registry_id = result['registryId']
        self._registry_name = resolve_encode(result['registryName'])
        self._url = resolve_encode(result['url'])
        self._image = resolve_encode(result['image'])
        self._tag = resolve_encode(result['tag'])

    @property
    def registry_id(self):
        return self._registry_id

    @property
    def registry_name(self):
        return self._registry_name

    @property
    def url(self):
        return self._url

    @property
    def image(self):
        return self._image

    @property
    def tag(self):
        return self._tag

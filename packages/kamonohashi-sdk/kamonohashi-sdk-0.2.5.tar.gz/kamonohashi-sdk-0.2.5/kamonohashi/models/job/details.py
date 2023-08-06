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
from kamonohashi.models.job.index import IndexModel
from kamonohashi.models.job.git_model import GitModelModel
from kamonohashi.models.job.container_image import ContainerImageModel

class DetailsModel(IndexModel):
    def __init__(self, result):
        super(DetailsModel, self).__init__(result)
        self.__options = resolve_encode(result['options'])
        git_model = result['gitModel']
        self.__git_model = None if git_model is None else GitModelModel(git_model)
        container = result['containerImage']
        self.__container = None if container is None else ContainerImageModel(container)
        self.__eval_argument = resolve_encode(result['evalArgument'])
        self.__completed_at = resolve_encode(result['completedAt'])
        self.__log_summary = resolve_encode(result['logSummary'])
        self.__parent = resolve_encode(result['parent'])
        self.__cpu = resolve_encode(result['cpu'])
        self.__memory = resolve_encode(result['memory'])
        self.__gpu = resolve_encode(result['gpu'])
        self.__partition = resolve_encode(result['partition'])
        self.__status = resolve_encode(result['status'])

    @property
    def options(self):
        return self.__options

    @property
    def git_model(self):
        return self.__git_model

    @property
    def container(self):
        return self.__container

    @property
    def eval_argument(self):
        return self.__eval_argument

    @property
    def completed_at(self):
        return self.__completed_at

    @property
    def log_summary(self):
        return self.__log_summary

    @property
    def parent(self):
        return self.__parent

    @property
    def cpu(self):
        return self.__cpu

    @property
    def memory(self):
        return self.__memory

    @property
    def gpu(self):
        return self.__gpu

    @property
    def partition(self):
        return self.__partition

    @property
    def status_detail(self):
        return self.__status_detail

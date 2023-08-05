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


class BranchModel(object):
    def __init__(self, result):
        self.__branch_name = resolve_encode(result['branchName'])
        self.__commit_id = resolve_encode(result['commitId'])

    @property
    def branch_name(self):
        return self.__branch_name

    @property
    def commit_id(self):
        return self.__commit_id

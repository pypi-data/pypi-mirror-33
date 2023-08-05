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


from __future__ import print_function, absolute_import, unicode_literals, with_statement

from kamonohashi.rest_call.util._kqi_http_client import KqiHttpClient
from kamonohashi.rest_call.util._parse_helper import parse_content
from kamonohashi.util._module_logger import get_logger

from kamonohashi.models.git.repository import RepositoryModel
from kamonohashi.models.git.branch import BranchModel
from kamonohashi.models.git.commit import CommitModel


class GitCall(object):
    def __init__(self, user_info):
        self.logger = get_logger(__name__)
        self.user_info = user_info
        self.http_client = KqiHttpClient(server=self.user_info.server, token=self.user_info.token,
                                         timeout=self.user_info.timeout, retry=self.user_info.retry)

    def _get_all_repositories(self):
        """Get all repositories

        :rtype: list[RepositoryModel]
        :return:
        """
        api = '/api/v1/git/repos'
        response = self.http_client.api_get(api)
        result = [RepositoryModel(x) for x in parse_content(response.content)]
        return result

    def _get_branches(self, owner, repository):
        """Get branches

        :param owner:
        :param repository:
        :rtype: list[BranchModel]
        :return:
        """
        api = '/api/v1/git/repos/{owner}/{repositoryName}/branches'.format(owner=owner, repositoryName=repository)
        response = self.http_client.api_get(api)
        result = [BranchModel(x) for x in parse_content(response.content)]
        return result

    def _get_commits(self, owner, repository, branch):
        """Get commits

        :param owner:
        :param repository:
        :param branch:
        :rtype: list[CommitModel]
        :return:
        """
        api = '/api/v1/git/repos/{owner}/{repositoryName}/commits'.format(
            owner=owner,
            repositoryName=repository
        )
        payload = {'branch': branch}
        response = self.http_client.api_get(api, False, payload)
        result = [CommitModel(x) for x in parse_content(response.content)]
        return result

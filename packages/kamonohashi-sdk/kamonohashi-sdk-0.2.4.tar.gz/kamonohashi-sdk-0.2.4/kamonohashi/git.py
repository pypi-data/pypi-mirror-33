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


from __future__ import print_function, absolute_import, with_statement

from kamonohashi.rest_call._git_call import GitCall
from kamonohashi.util._module_logger import get_logger
from kamonohashi.util._sdk_base import SdkBase

from kamonohashi.models.git.branch import BranchModel
from kamonohashi.models.git.repository import RepositoryModel
from kamonohashi.models.git.commit import CommitModel


class Git(SdkBase):
    def __init__(self, server, token=None, user=None, password=None, tenant=None,
                 timeout=None, retry=5):
        """

        :param server:
        :param token:
        :param user:
        :param password:
        :param tenant:
        :param timeout:
        :param retry:
        """
        super(Git, self).__init__(server=server, token=token, user=user, password=password, tenant=tenant,
                                  timeout=timeout, retry=retry)
        self.logger = get_logger(__name__)
        self.git_call = GitCall(self._user_info)

    def get_all_repositories(self):
        """Get all repositories

        :rtype: list[RepositoryModel]
        :return:
        """
        result = self.git_call._get_all_repositories()
        return result

    def get_branches(self, owner, repository):
        """Get branches

        :param owner:
        :param repository:
        :rtype: list[BranchModel]
        :return:
        """
        result = self.git_call._get_branches(owner, repository)
        return result

    def get_commits(self, owner, repository, branch):
        """Get commits

        :param owner:
        :param repository:
        :param branch:
        :rtype: list[CommitModel]
        :return:
        """
        result = self.git_call._get_commits(owner, repository, branch)
        return result

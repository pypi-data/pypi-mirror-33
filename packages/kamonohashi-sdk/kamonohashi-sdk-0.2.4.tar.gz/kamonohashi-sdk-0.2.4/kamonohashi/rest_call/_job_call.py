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

from kamonohashi.rest_call.util._kqi_http_client import KqiHttpClient
from kamonohashi.rest_call.util._parse_helper import parse_content
from kamonohashi.util._module_logger import get_logger

from kamonohashi.models.job.simple import SimpleModel
from kamonohashi.models.job.index import IndexModel
from kamonohashi.models.job.details import DetailsModel
from kamonohashi.models.job.attached_file_info import AttachedFileInfoModel
from kamonohashi.models.job.tensor_board import TensorBoardModel


class JobCall(object):
    def __init__(self, user_info):
        self.logger = get_logger(__name__)
        self.user_info = user_info
        self.http_client = KqiHttpClient(server=self.user_info.server, token=self.user_info.token,
                                         timeout=self.user_info.timeout, retry=self.user_info.retry)

    def _list_simple(self, query=None):
        """Get job list with simple format filtered by query

        :param query: Nullable search query
        :rtype: list[SimpleModel]
        """
        api = '/api/v1/jobs/simple'
        payload = {}
        if query is not None:
            payload = {'query': query}
        response = self.http_client.api_get(api, False, payload)
        response = [SimpleModel(x) for x in parse_content(response.content)]
        return response

    def _list(self, per_page, page, query=None):
        """Get job list filtered by query

        :param per_page:
        :param page:
        :param query:
        :rtype: list[IndexModel]
        """
        api = '/api/v1/jobs?perPage={0}&page={1}'.format(per_page, page)
        if query is not None:
            api = api + '&' + query
        response = self.http_client.api_get(api)
        result = [IndexModel(x) for x in parse_content(response.content)]
        return result

    def _get_total(self, query=None):
        """Get total count of whole job in a current tenant

        :param query:
        :rtype: int
        """
        api = '/api/v1/jobs/total'
        if query is not None:
            api = api + '?' + query
        result = self.http_client.api_get(api)
        return parse_content(result.content)

    def _get(self, id):
        """Get {id} job's detail.

        :param id:The id of the job
        :rtype: DetailsModel
        """
        api = '/api/v1/jobs/{0}'.format(id)
        response = self.http_client.api_get(api)
        result = DetailsModel(parse_content(response.content))
        return result

    def _get_log(self, id):
        """Get log file of {id} job

        :param id:
        :return: stream
        """
        api = '/api/v1/jobs/{0}/log'.format(id)
        response = self.http_client.api_get(api)
        return response

    def _create(self, name, registry_id, registry_image, registry_tag,
                dataset_id, train_argument, eval_argument, git_owner, git_repository,
                cpu, memory, gpu=None, partition=None, memo=None,
                git_branch=None, git_commit=None, parent_id=None, options=None):
        """Start a new job

        :param name:
        :param registry_id:
        :param registry_image:
        :param registry_tag:
        :param dataset_id:
        :param train_argument:
        :param eval_argument:
        :param git_owner:
        :param git_repository:
        :param cpu:
        :param memory:
        :param gpu:
        :param partition:
        :param memo:
        :param git_branch:
        :param git_commit:
        :param parent_id:
        :param options:
        :type options: dict
        :rtype: SimpleModel
        """
        api = '/api/v1/jobs'
        data = {
            'name': name,
            'containerImage': {
                'registryId': registry_id,
                'image': registry_image,
                'tag': registry_tag
            },
            'dataSetId': dataset_id,
            'parentId': parent_id,
            'gitModel': {
                'repository': git_repository,
                'owner': git_owner,
                'branch': git_branch,
                'commitId': git_commit
            },
            'trainArgument': train_argument,
            'evalArgument': eval_argument,
            'options': options,
            'cpu': cpu,
            'memory': memory,
            'gpu': gpu,
            'partition': partition,
            'memo': memo
        }
        response = self.http_client.api_post(api, data, True)
        result = SimpleModel(parse_content(response.content))
        return result

    def _update(self, id, memo):
        """Edit the job history.

        :param id:
        :param memo:
        :rtype: SimpleModel
        """
        api = '/api/v1/jobs/{0}'.format(id)
        data = {
            'memo': memo
        }
        response = self.http_client.api_patch(api, data, True)
        result = SimpleModel(parse_content(response.content))
        return result

    def _upload_files(self, id, train_log_name, train_log_path, trained_param_name, trained_param_path,
                      test_log_name=None, test_log_path=None, log_summary=None, gpu_driver=None):
        """Finish the job and save the results

        :param id:
        :param train_log_name:
        :param train_log_path:
        :param trained_param_name:
        :param trained_param_path:
        :param test_log_name:
        :param test_log_path:
        :param log_summary:
        :param gpu_driver:
        :rtype: SimpleModel
        """
        api = '/api/v1/jobs/{0}'.format(id)
        data = {
            'gpuDriver': gpu_driver,
            'trainLogName': train_log_name,
            'testLogName': test_log_name,
            'trainedParameterName': trained_param_name,
            'trainLogFileStorage': train_log_path,
            'trainedParameterFileStorage': trained_param_path,
            'testLogFileStorage': test_log_path,
            'logSummary': log_summary
        }
        response = self.http_client.api_put(api, data, True)
        result = SimpleModel(parse_content(response.content))
        return result

    def _list_attached_files(self, id, with_url):
        """Get file list

        :param id:
        :param bool with_url: if want to get download url true
        :rtype: list[AttachedFileInfoModel]
        """
        api = '/api/v1/jobs/{0}/files'.format(id)
        data = {
            'withUrl': with_url
        }
        response = self.http_client.api_get(api, False, data)
        result = [AttachedFileInfoModel(x) for x in parse_content(response.content)]
        return result

    def _create_attached_file(self, id, file_name, file_path):
        """Register attached file

        :param id:
        :param file_name:
        :param file_path:
        :rtype: AttachedFileInfoModel
        """
        api = '/api/v1/jobs/{0}/files'.format(id)
        data = {
            'fileName': file_name,
            'storedPath': file_path
        }
        response = self.http_client.api_post(api, data, True)
        result = AttachedFileInfoModel(parse_content(response.content))
        return result

    def _delete_attached_file(self, id, file_id):
        """Delete an attached file

        :param id:
        :param file_id:
        """
        api = '/api/v1/jobs/{0}/files/{1}'.format(id, file_id)
        self.http_client.api_delete(api)

    def _get_tensor_board(self, id):
        """Get tensor board container info

        :param id:
        :rtype: TensorBoardModel
        """
        api = '/api/v1/jobs/{0}/tensorboard'.format(id)
        response = self.http_client.api_get(api)
        result = TensorBoardModel(parse_content(response.content))
        return result

    def _create_tensor_board(self, id):
        """Run new tensor board container

        :param id:
        :rtype: TensorBoardModel
        """
        api = '/api/v1/jobs/{0}/tensorboard'.format(id)
        response = self.http_client.api_put(api, None, True)
        result = TensorBoardModel(parse_content(response.content))
        return result

    def _delete_tensor_board(self, id):
        """Delete tensor board container

        :param id: training-history id
        """
        api = '/api/v1/jobs/{0}/tensorboard'.format(id)
        self.http_client.api_delete(api)

    def _halt(self, id):
        """Halt a job

        :param id:A job id
        :rtype: SimpleModel
        """
        api = '/api/v1/jobs/{0}/halt'.format(id)
        response = self.http_client.api_post(api)
        result = SimpleModel(parse_content(response.content))
        return result

    def _complete(self, id):
        """Complete a job

        :param id:A job id
        :rtype: SimpleModel
        """
        api = '/api/v1/jobs/{0}/complete'.format(id)
        response = self.http_client.api_post(api)
        result = SimpleModel(parse_content(response.content))
        return result

    def _list_partitions(self):
        """ Get partition list

        :rtype: list[str]
        """
        api = '/api/v1/partitions'
        response = self.http_client.api_get(api)
        return parse_content(response.content)

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

from kamonohashi.rest_call._job_call import JobCall
from kamonohashi.util._object_storage import upload_file
from kamonohashi.util._object_storage import download_file
from kamonohashi.util._module_logger import get_logger
from kamonohashi.util._sdk_base import SdkBase

from kamonohashi.models.job.simple import SimpleModel
from kamonohashi.models.job.index import IndexModel
from kamonohashi.models.job.details import DetailsModel
from kamonohashi.models.job.attached_file import AttachedFileModel
from kamonohashi.models.job.attached_file_info import AttachedFileInfoModel
from kamonohashi.models.job.tensor_board import TensorBoardModel


class Job(SdkBase):
    def __init__(self, server, token=None, user=None, password=None, tenant=None,
                 timeout=30, retry=5):
        """Set logger and user_info

        :param server:
        :param token:
        :param user:
        :param password:
        :param tenant:
        :param timeout:
        :param retry:
        """
        super(Job, self).__init__(server=server, token=token, user=user, password=password, tenant=tenant,
                                  timeout=timeout, retry=retry)
        self.logger = get_logger(__name__)
        self.job_call = JobCall(self._user_info)

    def list_simple(self, query=None):
        """Get training histories with simple format filtered by query

        :param query:
        :rtype: list[SimpleModel]
        """
        self.logger.info('list job histories with simple form.')
        result = self.job_call._list_simple(query)
        return result

    def list(self, count, query=None):
        """Get training histories filtered by query

        :param count: the maximum number of result
        :param query:
        :rtype: list[IndexModel]
        """
        self.logger.info('Listing job histories.')
        per_page = count if count else 30
        result = self.job_call._list(per_page, 1, self._generate_query(query))
        return result

    def get_total(self, query=None):
        """Get total

        :param query:
        :rtype: int
        :return: total
        """
        self.logger.info('Getting total number of job histories.')
        result = self.job_call._get_total(self._generate_query(query))
        return result

    def get(self, id):
        """Get training history in detail

        :param id:
        :rtype: DetailsModel
        """
        self.logger.info('Getting job history {0}.'.format(id))
        result = self.job_call._get(id)
        return result

    def download_log(self, id):
        """Get stdout(stderr) log file in the training container

        :param id:
        :return: stream
        """
        self.logger.info('Downloading log files of job history {0}.'.format(id))
        result = self.job_call._get_log(id)
        return result

    def create(self, name, registry_image, registry_tag,
               dataset_id, train_argument, git_owner, git_repository,
               cpu, memory, gpu=None, partition=None, memo=None, eval_argument=None,
               git_branch=None, git_commit=None, parent_id=None, options=None):
        """Run new training

        :param name:
        :param registry_image:
        :param registry_tag:
        :param dataset_id:
        :param train_argument:
        :param eval_argument:
        :param git_owner: name of repository owner for job/eval model
        :param git_repository: name of repository for job/eval model
        :param cpu: allocate cpu core num
        :param memory: allocate memory size (GiB)
        :param gpu: allocate gpu num
        :param partition:
        :param memo:
        :param git_branch:
        :param git_commit:
        :param parent_id: parent training history id
        :param options: key value pair of environment variable in the container
        :type options: dict
        :rtype: SimpleModel
        """
        self.logger.info('Run a new job.')
        result = self.job_call._create(name, None, registry_image, registry_tag,
                                         dataset_id, train_argument, eval_argument, git_owner, git_repository,
                                         cpu, memory, gpu, partition, memo,
                                         git_branch, git_commit, parent_id, options)
        self.logger.info('Done')
        return result

    def update(self, id, memo=None):
        """Edit training

        :param id:
        :param memo:
        :rtype: SimpleModel
        """
        self.logger.info('Updating data')
        result = self.job_call._update(id, memo)
        self.logger.info('Done')
        return result

    def upload_files(self, id, train_log_path, trained_parameter_path,
                     test_log_path=None, log_summary=None, gpu_driver=None):
        """Complete training and upload result

        :param id:
        :param train_log_path:
        :param trained_parameter_path:
        :param test_log_path:
        :param log_summary:
        :param gpu_driver:
        :rtype: SimpleModel
        """
        self.logger.info('Start uploading result files.')
        self.logger.info('Uploading job log file.')
        train_log_info = upload_file(self._user_info, train_log_path, 'TrainLogs')
        self.logger.info('Uploading parameter file.')
        trained_param_info = upload_file(self._user_info, trained_parameter_path, 'TrainedParameters')
        if test_log_path is not None:
            self.logger.info('Uploading test log file.')
            test_log_info = upload_file(self._user_info, test_log_path, 'TestLogs')
            self.logger.info('Registering meta information.')
            result = self.job_call._upload_files(id, train_log_info.file_name, train_log_info.file_path,
                                                 trained_param_info.file_name, trained_param_info.file_path,
                                                 test_log_info.file_name, test_log_info.file_path, log_summary,
                                                 gpu_driver)
        else:
            self.logger.info('Registering meta information.')
            result = self.job_call._upload_files(id, train_log_info.file_name, train_log_info.file_path,
                                                 trained_param_info.file_name, trained_param_info.file_path,
                                                 None, None, log_summary, gpu_driver)
        self.logger.info('Done')
        return result

    def list_attached_files(self, id, with_url=False):
        """Get attached file list of the training history

        :param id:
        :param with_url: include the URL for download in the response
        :type with_url: bool
        :rtype: list[AttachedFileInfoModel]
        """
        self.logger.info('Listing attached files of the job history {0}.'.format(id))
        result = self.job_call._list_attached_files(id, with_url)
        return result

    def download_attached_files(self, id):
        """Get files

        :param id:
        :rtype: list[AttachedFileModel]
        :return:
        """
        self.logger.info('Start downloading files attached to job history {0}.'.format(id))

        models = []

        # URL付きで添付ファイル情報を取得
        self.logger.info('Checking meta info to download')
        result = self.job_call._list_attached_files(id, True)

        for model in result:
            self.logger.info('Downloading {0} file: {1}.'.format(model.key, model.file_name))
            result = download_file(model.file_name, model.url)
            models.append(AttachedFileModel(model, result.stream))
        return models

    def upload_attached_file(self, id, file_path):
        """Attach training history file

        :param id: existing training history id
        :param file_path:
        :rtype: AttachedFileInfoModel
        """
        self.logger.info('Uploading a file of job history {0}.'.format(id))
        file_info = upload_file(self._user_info, file_path, 'TrainingHistoryAttachedFiles')
        self.logger.info('Registering meta information.')
        result = self.job_call._create_attached_file(id, file_info.file_name, file_info.file_path)
        self.logger.info('Done')
        return result

    def delete_attached_file(self, id, file_id):
        """Delete attached job history file

        :param id:
        :param file_id:
        """
        self.logger.info('Deleting attached file {0} of training history {1}.'.format(file_id, id))
        self.job_call._delete_attached_file(id, file_id)
        self.logger.info('Done')

    def get_tensor_board(self, id):
        """Get tensor board container info

        :param id:
        :rtype: TensorBoardModel
        """
        self.logger.info('Getting tensor board container info of job history {0}.'.format(id))
        result = self.job_call._get_tensor_board(id)
        return result

    def create_tensor_board(self, id):
        """Run tensor board container

        :param id:
        :rtype TensorBoardModel
        :return:
        """
        self.logger.info('Running tensor board container for job history {0}.'.format(id))
        result = self.job_call._create_tensor_board(id)
        self.logger.info('Done')
        return result

    def delete_tensor_board(self, id):
        """Delete tensor board

        :param id:
        """
        self.logger.info('Deleting tensor board container for job history {0}.'.format(id))
        self.job_call._delete_tensor_board(id)
        self.logger.info('Done')

    def halt(self, id):
        """Halt a job forcibly

        :param id:
        :rtype SimpleModel
        """
        self.logger.info('Halt a job container {0} forcibly.'.format(id))
        result = self.job_call._halt(id)
        self.logger.info('Done')
        return result

    def complete(self, id):
        """Complete a job

        :param id:
        :rtype SimpleModel
        """
        self.logger.info('Complete a job container {0}.'.format(id))
        result = self.job_call._complete(id)
        self.logger.info('Done')
        return result

    def list_partitions(self):
        """List partitions in the cluster

         :rtype List[str]
         """
        self.logger.info('Listing partitions.')
        result = self.job_call._list_partitions()
        return result
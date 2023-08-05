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

import math
import os
from os import path

from tqdm import tqdm

from kamonohashi.models.dataset.data_type import DataTypeModel
from kamonohashi.models.dataset.details import DetailsModel
from kamonohashi.models.dataset.downloaded_dataset_entry import DownloadedDataSetEntryModel
from kamonohashi.models.dataset.index import IndexModel
from kamonohashi.rest_call._dataset_call import DataSetCall
from kamonohashi.util._encoder import resolve_encode
from kamonohashi.util._module_logger import get_logger
from kamonohashi.util._object_storage import download_file
from kamonohashi.util._sdk_base import SdkBase


class DataSet(SdkBase):
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
        super(DataSet, self).__init__(server=server, token=token, user=user, password=password, tenant=tenant,
                                      timeout=timeout, retry=retry)
        self.logger = get_logger(__name__)
        self.dataset_call = DataSetCall(self._user_info)

    def list(self, count, query=None):
        """Get dataset list filtered by query

        :param count: the maximum number of result
        :param query:
        :rtype: list[IndexModel]
        """
        self.logger.info('Listing dataset.')
        per_page = count if count else 30
        result = self.dataset_call._list(per_page, 1, self._generate_query(query))
        return result

    def get_total(self, query=None):
        """Get total

        :param query:
        :rtype: int
        :return: total
        """
        self.logger.info('Getting total number of dataset.')
        result = self.dataset_call._get_total(self._generate_query(query))
        return result

    def get(self, id):
        """Get dataset in detail

        :param id:
        :rtype: DetailsModel
        """
        self.logger.info('Getting dataset {0}.'.format(id))
        result = self.dataset_call._get(id)
        return result

    def get_as_json(self, id):
        """Get dataset in detail in json format

        :param id:
        :rtype: DetailModel
        """
        self.logger.info('Getting dataset {0} in json format.'.format(id))
        result = self.dataset_call._get_as_raw(id)
        return result

    def create(self, dic):
        """Create dataset from valid dictionary

        :param: dict dic:
        :rtype: IndexModel
        :return:
        """
        self.logger.info('Creating dataset.')
        result = self.dataset_call._create(dic)
        self.logger.info('Done')
        return result

    def update(self, id, dic):
        """Update dataset entries

        :param id:
        :param dict dic:
        :rtype: IndexModel
        """
        self.logger.info('Updating dataset')
        result = self.dataset_call._update(id, dic)
        self.logger.info('Done')
        return result

    def update_meta_info(self, id, name, memo):
        """Update dataset meta information

        :param id:
        :param name:
        :param memo:
        :rtype: IndexModel
        """
        self.logger.info('Updating dataset meta info')
        result = self.dataset_call._update_meta_info(id, name, memo)
        self.logger.info('Done')
        return result

    def delete(self, id):
        """Delete dataset

        :param id:
        """
        self.logger.info('Deleting data {0}.'.format(id))
        self.dataset_call._delete(id)
        self.logger.info('Done')

    def download_files(self, id):
        """Get data files in the dataset as stream

        :param id: dataset id
        :rtype: list[DownloadedDataSetEntryModel]
        """
        self.logger.info('Downloading all data files of dataset {0}.'.format(id))
        result = self.dataset_call._list_files(id)
        download_files = list()
        for entry in result.entries:
            for file_info in entry.files:
                item = DownloadedDataSetEntryModel(entry.type, file_info.key, file_info.id,
                                                   download_file(file_info.name, file_info.url))
                download_files.append(item)
        return download_files

    def download_and_save_files(self, id, dst_root):
        """download and save dataset-files to dst_root

        :param id: dataset id
        :rtype: list[DownloadedDataSetEntryModel]
        """
        self.logger.info('Downloading all data files of dataset {0} to {1}.'.format(id, dst_root))
        result = self.dataset_call._list_files(id)
        download_files = list()
        for entry in result.entries:
            for file_info in entry.files:
                downloaded_file_model = download_file(file_info.name, file_info.url)
                dst = os.path.join(dst_root, entry.type, file_info.key, str(file_info.id))
                save_file(dst, file_info.name, downloaded_file_model.stream)

        return download_files

    def list_datatypes(self):
        """Get data types

        :rtype: list[DataTypeModel]
        """
        self.logger.info('Listing data types.')
        result = self.dataset_call._list_datatypes()
        return result

def save_file(dst, name, stream):
    """save a file from stream data

    :param str dst: destination path to save file
    :param name:
    :param stream:
    :return:
    """
    # Pythonの最低な仕様のため、2ではxが使えないため上書きを許可するwを使うこととする
    # with open(path.join(dst, model.name), 'xb') as f:
    chunk_size = 1024
    p = path.abspath(dst)
    if not path.exists(p):
        os.makedirs(p)
    print('Downloading {0}'.format(name))
    with tqdm(total=math.ceil(len(stream.content) * 1.0 / chunk_size)) as pbar:
        with open(path.join(resolve_encode(p), name), 'wb') as f:
            for chunk in stream.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                pbar.update(1)


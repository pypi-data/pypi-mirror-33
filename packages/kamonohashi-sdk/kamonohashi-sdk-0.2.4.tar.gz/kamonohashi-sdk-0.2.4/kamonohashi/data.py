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

import os

from kamonohashi.exception import KqiError
from kamonohashi.models.data.details import DetailsModel
from kamonohashi.models.data.file_info import FileInfoModel
from kamonohashi.models.data.index import IndexModel
from kamonohashi.rest_call._data_call import DataCall
from kamonohashi.util._module_logger import get_logger
from kamonohashi.util._object_storage import download_file
from kamonohashi.util._object_storage import upload_file
from kamonohashi.util._sdk_base import SdkBase


class Data(SdkBase):
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
        super(Data, self).__init__(server=server, token=token, user=user, password=password, tenant=tenant,
                                   timeout=timeout, retry=retry)
        self.logger = get_logger(__name__)
        self.data_call = DataCall(self._user_info)

    def list_simple(self, query=None):
        """Get data list with simple format filtered by query

        :param query:
        :rtype: list[SimpleModel]
        """
        self.logger.info('Listing data with simple form.')
        result = self.data_call._list_simple(query)
        return result

    def list(self, count, query=None):
        """Get data list filtered by query

        :param count: the maximum number of result
        :param query:
        :rtype: list[IndexModel]
        """
        self.logger.info('Listing data.')
        per_page = count if count else 30
        result = self.data_call._list(per_page, 1, self._generate_query(query))
        return result

    def get_total(self, query=None):
        """Get total

        :param query:
        :rtype: int
        :return: total
        """
        self.logger.info('Getting total number of data.')
        result = self.data_call._get_total(self._generate_query(query))
        return result

    def get(self, id):
        """Get data in detail

        :param id:
        :rtype: DetailsModel
        """
        self.logger.info('Getting data {0}.'.format(id))
        result = self.data_call._get(id)
        return result

    def create(self, name, data_file, annotation_file=None, memo=None, tags=None):
        """Create data

        :param name:
        :param data_file: path to a data file
        :param annotation_file: path to an annotation file
        :param memo:
        :param tags:
        :rtype: IndexModel
        """
        # TODO: フォルダの存在処理とかを追加（ppでも同じようなことやってるから、なにかモジュールにまとめよう）
        self.logger.info('Start creating data.')
        if not os.path.exists(data_file):
            raise KqiError('{0} is not exist'.format(data_file))
        # 最初に画像ファイルをアップロード
        self.logger.info('Uploading image file.')
        data_info = upload_file(self._user_info, data_file, 'Data')
        # 続いてアノテーションファイルがあればアップロード
        if annotation_file:
            if not os.path.exists(annotation_file):
                raise KqiError('{0} is not exist'.format(annotation_file))
            self.logger.info('Uploading annotation file.')
            annotation_info = upload_file(self._user_info, annotation_file, 'Data')
            self.logger.info('Registering meta information.')
            result = self.data_call._create(name,
                                            data_info.file_name,
                                            data_info.file_path,
                                            annotation_info.file_name,
                                            annotation_info.file_path,
                                            memo, tags)
        else:
            self.logger.info('Registering meta information.')
            result = self.data_call._create(name=name,
                                            image_name=data_info.file_name,
                                            image_path=data_info.file_path,
                                            memo=memo,
                                            tags=tags)
        self.logger.info('Done')
        return result

    def update(self, id, memo=None, tags=None):
        """Edit data

        :param id:
        :param memo:
        :param tags:
        :rtype: IndexModel
        """
        self.logger.info('Updating data')
        result = self.data_call._update(id, memo, tags)
        self.logger.info('Done')
        return result

    def delete(self, id):
        """Delete data

        :param id:
        """
        self.logger.info('Deleting data {0}.'.format(id))
        self.data_call._delete(id)
        self.logger.info('Done')

    def list_files(self, id):
        """Get data list filtered by query

        :param id: data id
        :rtype: list[FileInfoModel]
        """
        self.logger.info('Listing files of data {0}.'.format(id))
        result = self.data_call._list_files(id)
        return result

    def download_file(self, id, key):
        """Get data file as stream

        :param id:
        :param key: designate 'Image' or 'Annotation'
        :rtype: DownloadedFileModel
        :return:
        """
        self.logger.info('Start downloading {0} file of data {1}.'.format(key, id))
        self.logger.info('Checking meta info to download')
        info = self.data_call._get_file_info(id, key)
        self.logger.info('Downloading file: {0}.'.format(info.name))
        result = download_file(info.name, info.url)
        return result

    def upload_file(self, id, file_path, key):
        """Upload and Register data file

        :param id: existing data id
        :param file_path:
        :param key: designate 'Image' or 'Annotation'
        :rtype: FileInfoModel
        :return:
        """
        self.logger.info('Uploading {0} file of data {1}.'.format(key, id))
        if not os.path.exists(file_path):
            raise KqiError('{0} is not exist'.format(file_path))
        annotation_info = upload_file(self._user_info, file_path, 'Data')
        self.logger.info('Registering meta information.')
        result = self.data_call._create_file_info(id, annotation_info.file_name, key, annotation_info.file_path)
        self.logger.info('Done')
        return result

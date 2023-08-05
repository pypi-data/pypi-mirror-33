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
"""
ObjectStorageと直接通信を管理するクラス
"""

from __future__ import print_function, absolute_import, unicode_literals, with_statement

import math
import os

from kamonohashi.models.downloaded_file import DownloadedFileModel
from kamonohashi.rest_call._storage_call import StorageCall
from kamonohashi.util._http_client import HttpClient
from kamonohashi.util._module_logger import get_logger
from tqdm import tqdm

logger = get_logger(__name__)

# TODO:ここだけasyncioとaiohttpを使った非同期request実装にしてもいいかも


class UploadedInfoModel(object):
    def __init__(self, file_name, file_path):
        self.__file_name = file_name
        self.__file_path = file_path

    @property
    def file_name(self):
        return self.__file_name

    # file_pathだと端末側と間違えかねないので変えたい   
    @property
    def file_path(self):
        return self.__file_path


def __split_file(file, byte_size, part_sum):
    """Split file size per byte size

    :param file:
    :param byte_size:
    :param part_sum:
    :return:
    """
    with open(file, 'rb') as f:
        for _ in range(part_sum):
            data = f.read(byte_size)
            yield data


def upload_file(user_info, file_path, file_type, partition_mb_size=100):
    """Multi part upload

    :param user_info: kqiとの接続に使用するユーザ情報
    :type user_info: UserInfo
    :param file_path:
    :param file_type:
    :param partition_mb_size:
    :rtype UploadedInfoModel
    :return: {'file_name': str, 'file_path': str}
    """
    # TODO: implement async upload

    storage_call = StorageCall(user_info)

    byte_size = partition_mb_size * 1024 ** 2
    part_sum = int(math.ceil(os.stat(file_path).st_size*1.0 / byte_size))

    logger.info('Getting pre signed url')
    upload_info = storage_call._get_upload_parameter(file_path, file_type, part_sum)
    logger.info('Got pre signed url')

    logger.info('Uploading data')
    cnt = 0
    part_info = []
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    # Cephへのアクセス用に、引数なしで新規HTTP Clientを作成
    http_client = HttpClient()

    with tqdm(total=part_sum) as pbar:
        for data in __split_file(file_path, byte_size, part_sum):
            logger.info('uploading part{cnt}'.format(cnt=cnt+1))
            result = http_client.put(upload_info.urls[cnt], data=data, headers=headers)
            etag = result.headers['ETag']
            logger.info('uploaded part{cnt}'.format(cnt=cnt+1))
            cnt += 1
            pbar.update(1)
            part_info.append(cnt.__str__() + '+' + etag)
    complete_model = {'UploadId': upload_info.upload_id,
                      'PartETags': part_info,
                      'Key': upload_info.key}
    logger.info('Uploaded data')

    logger.info('Sending finish operation')
    storage_call._complete_multi_upload(complete_model)
    logger.info('Done: uploaded data')
    return UploadedInfoModel(upload_info.file_name, upload_info.file_path)


def download_file(name, url):
    """
    download file data as DownloadedFileModel
    :param name: file name
    :param url: download url
    :rtype: DownloadedFileModel
    """
    http_client = HttpClient()
    return DownloadedFileModel(name, http_client.get(url, True))

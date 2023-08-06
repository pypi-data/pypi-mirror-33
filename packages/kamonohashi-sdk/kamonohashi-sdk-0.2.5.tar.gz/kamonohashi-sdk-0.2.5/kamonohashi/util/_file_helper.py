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
import os

from kamonohashi.util._module_logger import get_logger

logger = get_logger(__name__)


def write_chunk(file_path, stream, chunk_byte=1024):
    with open(file_path, 'wb+') as file:
        for chunk in stream(chunk_size=chunk_byte):
            if chunk:
                file.write(chunk)


def read_chunk(file_path, part_sum, chunk_mbyte=500):
    chunk_byte = chunk_mbyte * 1024 ** 2
    with open(file_path, 'rb') as f:
        for i in range(part_sum):
            chunk = f.read(chunk_byte)
            # ファイルサイズが大きい場合に対応するため、generatorにする
            yield chunk


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

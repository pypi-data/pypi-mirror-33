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
結果のコンソール出力の支援関数群。
基本はデータを整形して表示するメソッドたち。
"""

from terminaltables import AsciiTable


def table(data):
    """
    指定したデータを表形式で標準出力する
    :param data:
    :return:
    """
    if len(data) == 0:
        print('No data')
        return
    image_keys = [data[0].get_header()]
    for d in data:
        image_keys.append(d.to_array())
    result_table = AsciiTable(image_keys)
    print(result_table.table)

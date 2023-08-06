# Copyright 2018 Locl Interactive Inc. (d/b/a Meya.ai). All Rights Reserved.
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

from __future__ import print_function
from __future__ import absolute_import

import os

from meya_cli.base_command import BaseCommand
from meya_cli.path_utils import has_hidden_component


class ListCommand(BaseCommand):
    INVOCATION = "list"
    DESCRIPTION = "List remote files. By default, these files are " \
                  "downloaded with 'meya-cli download' or uploaded " \
                  "from local copies with 'meya-cli upload'."
    ARGUMENTS = [
        ("--local-diff", {"help": "list files only present locally.",
                          "action": 'store_true'}),
        ("--remote-diff", {"help": "list files only present on remote server.",
                           "action": 'store_true'}),
    ]

    def perform(self):
        if self.args.local_diff:
            remote_files = self.remote_files()
            for path in self.local_files():
                if path not in remote_files:
                    print(path)
        elif self.args.remote_diff:
            for path in self.remote_files():
                if not os.path.isfile(path):
                    print(path)
        else:
            for path in self.remote_files():
                print(path)

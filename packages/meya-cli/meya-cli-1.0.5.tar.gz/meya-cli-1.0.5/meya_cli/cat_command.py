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


class CatCommand(BaseCommand):
    INVOCATION = "cat"
    DESCRIPTION = "Show the contents of remote files."
    ARGUMENTS = [
        ("files", {"nargs": "+", "help": "files to show on standard output."})
    ]

    def perform(self):
        for file in self.args.files:
            abs_path = os.path.abspath(file)
            meya_path = os.path.relpath(abs_path,
                                        start=self.config.root_dir)
            result = self.api.get(self.file_api_root + meya_path)
            print(result["contents"])

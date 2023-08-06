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
from meya_cli.meya_api import MeyaNoSuchFileException


class DeleteCommand(BaseCommand):
    INVOCATION = "delete"
    DESCRIPTION = "Delete Meya bot source from a Meya-managed folder. " \
                  "Deletes given bot files on Meya (but not locally)"
    ARGUMENTS = [
        ("--remote-diff", {"help": "delete files only found in remote bot.",
                           "action": 'store_true'}),
        ("--local-diff", {"help": "delete files only found in local bot. "
                                  "WARNING: Deletes local files",
                          "action": 'store_true'}),
        ("files", {"help": "file to delete in Meya bot source "
                           "(local copy preserved)",
                   "nargs": "*"})
    ]

    def delete(self, path):
        meya_path = os.path.relpath(path, start=self.config.root_dir)
        rel_path = os.path.relpath(path)
        print("Deleting remote " + rel_path)
        try:
            self.api.delete(self.file_api_root + meya_path)
        except MeyaNoSuchFileException:
            print("No remote file matching " + meya_path + "; skipping.")

    def perform(self):
        if self.args.files and self.args.remote_diff:
            raise Exception("Cannot specify both 'remote_diff' and a "
                            "list of files.")
        if self.args.files and self.args.local_diff:
            raise Exception("Cannot specify both 'local_diff' and a "
                            "list of files.")
        if self.args.remote_diff:
            # delete all files not found locally
            files = []
            for file in self.remote_files():
                if not os.path.isfile(file):
                    files.append(file)
            if not files:
                print("No remote-only files to be deleted.")
        elif self.args.local_diff:
            # delete all files ONLY found locally
            files = []
            remote_files = self.remote_files()
            for path in self.local_files():
                if path not in remote_files:
                    files.append(path)
            if not files:
                print("No local-only files to be deleted.")
            for file in files:
                print("Deleting local " + file)
                os.unlink(file)
            return
        else:
            # delete all files specified
            files = self.args.files
            if not files:
                print("No files specified for deletion.")
        for file in files:
            path = os.path.abspath(file)
            self.delete(path)

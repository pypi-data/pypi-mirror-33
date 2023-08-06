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
import re

from meya_cli.base_command import BaseCommand
from meya_cli.meya_api import MeyaFileTooBigException
from meya_cli.meya_config import MEYA_CONFIG_FILE
from meya_cli.path_utils import has_hidden_component

TOO_BIG_REGEX = re.compile(".*Ensure this field has no more "
                           "than .* characters.*")


class UploadCommand(BaseCommand):
    INVOCATION = "upload"
    DESCRIPTION = "Update Meya bot source from a Meya-managed folder. " \
                  "Uploads a single bot file, if " \
                  "given, or the entire bot source otherwise."
    ARGUMENTS = [
        ("files", {"nargs": "*", "help": "files to upload (uploads "
                                         "all files if not present)"})
    ]

    def _upload(self, path):
        meya_path = os.path.relpath(path, start=self.config.root_dir)
        rel_path = os.path.relpath(path)
        if os.path.isdir(path):
            self._upload_all(path)
            return
        if not self.config.should_upload_path(path):
            return

        print("Uploading " + rel_path)
        with open(path, 'r') as f:
            try:
                self.api.post(self.file_api_root + meya_path,
                              {"contents": f.read()})
            except MeyaFileTooBigException:
                print("SKIPPING " + os.path.relpath(path) +
                      ", file too large to upload. Consider adding to " +
                      "'ignore_files' in '" + MEYA_CONFIG_FILE + "'.")

    def _upload_files(self, files):
        if not files:
            print("Nothing to update! You can explicitly "
                  "upload new files by providing them with "
                  "meya-cli upload <files>.")
        regular_uploads = []
        delayed_uploads = []
        for file in files:
            # make sure intents.yaml is uploaded last (dependent on flows being
            # added!)
            if file.endswith("intents.yaml"):
                delayed_uploads.append(file)
            else:
                regular_uploads.append(file)
        for file in regular_uploads:
            self._upload(file)
        for file in delayed_uploads:
            self._upload(file)

    def _upload_all(self, folder):
        paths = []
        for dir, _child_dirs, files in os.walk(folder):
            for file in files:
                path = os.path.join(dir, file)
                if self.config.ignore_dot_files and has_hidden_component(path):
                    continue
                if not self.config.path_matches_autosync_patterns(path):
                    continue
                paths.append(path)
        self._upload_files(paths)

    def perform(self):
        if self.args.files:
            self._upload_files([os.path.abspath(file)
                                for file in self.args.files])
        else:
            # TODO efficiency for folders with tons of files
            self._upload_all(os.path.abspath("."))

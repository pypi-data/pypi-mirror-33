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


from meya_cli.base_command import BaseCommand


class WatchCommand(BaseCommand):
    INVOCATION = "watch"
    DESCRIPTION = "Watch a Meya-managed folder, updating on file changes."
    ARGUMENTS = [
        ("files", {"nargs": "*", "help": "files to upload (uploads "
                                         "all files if not present)"})
    ]

    def perform(self):
        from meya_cli.fs_events import MeyaFileSystemEventHandler
        from watchdog.observers import Observer

        event_handler = MeyaFileSystemEventHandler(self.config)

        print("Watching " + self.config.root_dir)
        # start the observer
        observer = Observer()
        observer.schedule(event_handler, self.config.root_dir, recursive=True)
        observer.start()
        try:
            while True:
                event_handler.step(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

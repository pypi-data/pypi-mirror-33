#!/usr/bin/env python
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

import logging
import os
import sys

from meya_cli.cat_command import CatCommand
from meya_cli.delete_command import DeleteCommand
from meya_cli.download_command import DownloadCommand
from meya_cli.meya_api import MeyaAPIException
from meya_cli.meya_config import find_meya_config, MEYA_CONFIG_FILE
from meya_cli.upload_command import UploadCommand
from meya_cli.watch_command import WatchCommand
from meya_cli.list_command import ListCommand
from meya_cli.init_command import InitCommand


COMMAND_TYPES = [
    InitCommand,
    DownloadCommand,
    UploadCommand,
    WatchCommand,
    DeleteCommand,
    ListCommand,
    CatCommand
]


def valid_command_invocations():
    return [cls.INVOCATION for cls in COMMAND_TYPES] + ["help"]


def get_command(config, command_name, argv):
    for cls in COMMAND_TYPES:
        if command_name == cls.INVOCATION:
            return cls(config, argv)
    raise Exception("Unsupported command '" + command_name + "'!")


def configure_logger():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')


def print_generic_help(show_help):
    print("Manage Meya apps from command-line.")
    if not show_help:
        print("Full help: meya-cli help")
    for cls in COMMAND_TYPES:
        parser = cls.arg_parser()
        print("")
        print("-- " + cls.INVOCATION.upper() + ":")
        if show_help:
            parser.print_help()
        else:
            parser.print_usage()


def main():
    try:
        configure_logger()
        if len(sys.argv) <= 1:
            print_generic_help(False)
            return
        elif sys.argv[1] in ("help", "--help", "-h"):
            print_generic_help(True)
            return
        elif sys.argv[1] not in valid_command_invocations():
            print(
                "Error: '{command}' is not a valid command! "
                "See usage below.\n".format(
                    command=sys.argv[1]
                )
            )
            print_generic_help(False)
            return

        # common for all commands, need meya config
        start_path = os.path.abspath(".")
        config = find_meya_config(start_path)
        if not config and sys.argv[1] != "init":
            print(
                "Could not find '{config_file}' in '{path}' "
                "or any parent folders!".format(
                    config_file=MEYA_CONFIG_FILE,
                    path=start_path
                )
            )
            sys.exit(1)

        command = get_command(config, sys.argv[1], sys.argv[2:])
        command.perform()
    except MeyaAPIException as err:
        print(err)

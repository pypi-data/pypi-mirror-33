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

import re
import copy
import os
import requests

from meya_cli.meya_config import REST_API_VERSION, USER_AGENT_STRING


class MeyaAPIException(Exception):
    PATTERN = re.compile(".*")
    MESSAGE = None

    @classmethod
    def raise_if_match(cls, error):
        for error in error:
            if cls.PATTERN.match(error):
                raise cls(cls.MESSAGE or error)


class MeyaNoSuchFileException(MeyaAPIException):
    PATTERN = re.compile("No such.*file.*")


class MeyaFileTooBigException(MeyaAPIException):
    PATTERN = re.compile(".*Ensure this field has no more "
                         "than .* characters.*")


class MeyaInvalidAPIKey(MeyaAPIException):
    PATTERN = re.compile(".*Invalid API key.*")
    MESSAGE = "The API key you are trying to use is invalid. " \
              "Please check the API key of the bot you " \
              "intend to use on its Settings page."


class MeyaVersionUnsupported(MeyaAPIException):
    PATTERN = re.compile(".*API version.*exceeds.*")

    def __init__(self, message):
        super(MeyaVersionUnsupported, self).__init__(
            "Server reported: " + message + "\nmeya-cli is out of date. " +
            "Please run 'pip install --upgrade meya-cli'."
        )


ERROR_TYPES = [
    MeyaNoSuchFileException,
    MeyaFileTooBigException,
    MeyaInvalidAPIKey,
    MeyaVersionUnsupported,
    # generic error:
    MeyaAPIException
]


class MeyaAPI(object):
    REQUEST_TIMEOUT = 60

    def __init__(self, api_key, base_url, command_string=''):
        self.api_key = api_key
        self.base_url = base_url
        self.command_string = command_string

    def _add_metadata(self, base_json):
        json = copy.copy(base_json)
        json["version"] = REST_API_VERSION
        json["user_agent"] = USER_AGENT_STRING
        if self.command_string:
            # we send a minimal string representing the high-level command
            # for meya-cli adoption/usage analytics
            # (no user-identifying data passed here)
            json["command"] = self.command_string
        return json

    def _send_request(self, send_method, path, data={}):
        return send_method(
            os.path.join(self.base_url, path),
            # Can serve files:
            headers={'content-type': 'application/json'},
            json=self._add_metadata(data),
            auth=(self.api_key, None),
            timeout=self.REQUEST_TIMEOUT
        )

    def _handle_response(self, response):
        errors, warnings = self._parse_errors_and_warnings(response)
        if response.status_code < 200 or response.status_code >= 300:
            self._raise_error(errors, response)
        self._print_warnings(warnings)
        return response.json()

    def _parse_errors_and_warnings(self, response):
        try:
            response_data = response.json()
            errors = response_data.get("errors", [])
            if "detail" in response_data:
                errors.append(response_data["detail"])
            warnings = response_data.get("warnings", [])
        except ValueError:
            errors = []
            warnings = []

        return errors, warnings

    def _raise_error(self, errors, response):
        if not errors:
            if response.status_code == 404:
                errors = ["Got 404 from '" + response.request.url +
                          "'. This URL format might be incorrect, or an "
                          "incorrect 'api_root' might be set."]
            else:
                errors = ["Unexpected server error. Got back: " + response.text]
        for cls in ERROR_TYPES:
            cls.raise_if_match(errors)

    def _print_warnings(self, warnings):
        for warning in warnings:
            print(warning)

    def get(self, path):
        response = self._send_request(requests.get, path)
        return self._handle_response(response)

    def post(self, path, data):
        response = self._send_request(requests.post, path, data)
        return self._handle_response(response)

    def delete(self, path):
        response = self._send_request(requests.delete, path)
        return self._handle_response(response)

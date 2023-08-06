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

from setuptools import setup

setup(
    name='meya-cli',
    version='1.0.5',
    description='Manage Meya bots from command-line.',
    long_description='Manage Meya bots from command-line, enabling you to use your favourite tools while updating live on https://meya.ai. ',
    author='Meya.ai',
    author_email='support@meya.ai',
    packages=['meya_cli'],
    install_requires=[
        "watchdog==0.8.3",
        "requests==2.18.4",
        "poyo==0.4.1"
    ],
    entry_points={
        'console_scripts': [
            'meya-cli = meya_cli.meya_cli:main'
        ]
    },
    license='Apache License 2.0'
)

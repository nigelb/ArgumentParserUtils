# ArgumentParserUtils provides Utilities and helpers for Python's
# ArgumentParser.
#
# Copyright 2024 NigelB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

setup(name='ArgumentParserUtils',
      version='0.0.1',
      description="ArgumentParserUtils provides Utilities and helpers for Python's ArgumentParser.",
      author='NigelB',
      author_email='nigel.blair@gmail.com',
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
      ],
      extras_require =
      {
            "mqtt": ["paho_mqtt"],
            "serial": ["pyserial"],
            "modbus": ["pymodbus"],
            "mailgun": ["requests"],
      },
      entry_points={
          "console_scripts": [
          ]
      },
      )

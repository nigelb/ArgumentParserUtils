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

from argparse import ArgumentParser

from argparseutils.helpers.serialport import SerialHelper


def main():
    parser = ArgumentParser("SerialHelper Test")
    SerialHelper.add_parser_options(parser, baudrate=115200)

    args = parser.parse_args()

    serial_port = SerialHelper.create_serial(args)

if __name__ == '__main__':
    main()
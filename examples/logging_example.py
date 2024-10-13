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

import logging
from argparse import ArgumentParser

from argparseutils.helpers.pythonlogging import LoggingHelper


def main():
    parser = ArgumentParser("Logging Test")

    LoggingHelper.add_parser_options(parser, log_level='TRACE')

    args = parser.parse_args()

    LoggingHelper.init_logging(args)

    logger = logging.getLogger("Logging Test")
    logger.critical("This is a log message")
    logger.trace("A TRACE log message")


if __name__ == '__main__':
    main()
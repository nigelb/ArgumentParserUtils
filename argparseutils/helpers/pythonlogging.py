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
from argparse import ArgumentParser, Namespace
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional, List

from argparseutils.helpers.utils import add_option, fix_formatter_class

class LoggingHelper:
    def_fmt = "%(asctime)-15s %(process)-8d %(levelname)-7s %(name)s %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
    debug_def_fmt = "%(asctime)-15s %(process)-8d %(levelname)-7s %(name)s File \"%(pathname)s\", line %(lineno)d, in %(funcName)s - %(message)s"

    @classmethod
    def add_parser_options(cls, parser: ArgumentParser, **kwargs):
        fix_formatter_class(parser)

        _add_log_level("TRACE", 5)

        # parser.add_argument("--log-level", default=__get_env__("LOG_LEVEL", kwargs.get('log_level', 'INFO')),
        #                     choices=logging._nameToLevel.keys(), help="The log level to use.")
        add_option(parser, kwargs, name="log-level", author_default='INFO', choices=logging._nameToLevel.keys(),
                   help="The log level to use.")

    @classmethod
    def init_logging(cls, args: Namespace, format=def_fmt, filename=None):
        kwargs = dict(format=format, level=logging._nameToLevel[args.log_level], )
        if filename is not None:
            kwargs["filename"] = filename
        logging.basicConfig(**kwargs)

    @classmethod
    def init_logging_from_config(cls, config: 'LoggingConfig'):
        _add_log_level("TRACE", 5)
        logging.basicConfig(format=config.format, level=logging._nameToLevel[config.level])
        for lg in config.logger_configs:
            logging.getLogger(lg.name).setLevel(lg.level)

@dataclass
class LoggerConfig:
    name: str
    level: str

@dataclass
class LoggingConfig:
    format: Optional[str] = LoggingHelper.def_fmt
    level: Optional[str] = logging.getLevelName(logging.INFO)
    logger_configs: List[LoggerConfig] = field(default_factory=list)

    @staticmethod
    def from_dict(config: dict) -> 'LoggingConfig':
        local_copy = deepcopy(config)
        logger_configs = []
        if 'logger_configs' in local_copy:
            logger_configs = [LoggerConfig(**x) for x in local_copy['logger_configs']]
            local_copy['logger_configs'] = logger_configs
        return LoggingConfig(**local_copy)


def _add_log_level(name, level):
    setattr(logging, name.upper(), level)
    logging.addLevelName(level, name.upper())

    def base_log(msg, *args, **kwargs):
        logging.log(msg, *args, **kwargs)

    def level_log(self, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)

    setattr(logging, name.lower(), base_log)
    setattr(logging.getLoggerClass(), name.lower(), level_log)

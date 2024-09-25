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


from argparseutils.helpers.utils import __get_env__, fix_formatter_class, add_env_parser_options, handle_env_display


class LoggingHelper:
    def_fmt = "%(asctime)-15s %(process)-8d %(levelname)-7s %(name)s %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
    debug_def_fmt = "%(asctime)-15s %(process)-8d %(levelname)-7s %(name)s File \"%(pathname)s\", line %(lineno)d, in %(funcName)s - %(message)s"

    @classmethod
    def add_parser_options(cls, parser, env=None):
        fix_formatter_class(parser)
        add_env_parser_options(parser)

        if env is not None:
            env = {key: value.value for (key, value) in env.items()}
        _add_log_level("TRACE", 5)

        parser.add_argument("--log-level", default=__get_env__("LOG_LEVEL", 'INFO', env=env),
                            choices=logging._nameToLevel.keys(), help="The log level to use.")

    @classmethod
    def init_logging(cls, args, format=def_fmt, filename=None):
        handle_env_display(args)
        kwargs = dict(format=format, level=logging._nameToLevel[args.log_level],)
        if filename is not None:
            kwargs["filename"] = filename
        logging.basicConfig(**kwargs)


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

# ArgumentParserUtils provides Utilities and helpers for Python's
# ArgumentParser.
#
# Copyright [2024] [NigelB]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# Copyright 2024 NigelB
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from collections import defaultdict
from functools import lru_cache
from typing import Any
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def __get_env__(var_name: str, default: object, type: type = str, shard: str = "") -> object:
    """
    __get_env__ Looks up the value of the field `var_name` firstly in `env` secondly in the environmental
    variables then if`var_name` it is still not found returns the `default` value

    :param var_name: The variable to lookup in `env` and the in the environmental variables
    :param default: If the `var_name` variable is not found, return this value
    :param type: The type to convert the found value to
    :return: The found value or `default`
    """

    if len(shard.strip()) > 0:
        var_name = "%s_%s" % (shard.upper(), var_name.upper())
    
    get_environment_registry().register_env(var_name)
    
    if var_name in os.environ:
        return type(os.environ[var_name])
    elif default is not None:
        return type(default)

    return None


class CliShardWrapper:
    def __init__(self, args, shard):
        object.__setattr__(self, 'args', args)
        object.__setattr__(self, 'shard', shard)

    def __getattribute__(self, name: str) -> Any:
        args = object.__getattribute__(self, 'args')
        partition = object.__getattribute__(self, 'shard')
        _name_ = "%s_%s" % (partition, name)
        return args.__getattribute__(_name_)

    def __setattr__(self, name: str, value: Any) -> None:
        args = object.__getattribute__(self, 'args')
        partition = object.__getattribute__(self, 'shard')
        _name_ = "%s_%s" % (partition, name)
        args.__setattr__(_name_, value)


def get_shard_values(shard_name):
    cli_shard = ""
    help_shard = ""
    if len(shard_name) > 0:
        cli_shard = f"{shard_name}-"
        help_shard = f" [{shard_name}] "
    return cli_shard, help_shard


def fix_formatter_class(parser, formatter=ArgumentDefaultsHelpFormatter):
    if not isinstance(parser.formatter_class, ArgumentDefaultsHelpFormatter):
        parser.formatter_class = ArgumentDefaultsHelpFormatter


def get_args(args, shard):
    if len(shard) > 0:
        return CliShardWrapper(args, shard)
    return args


class ShardRegistry:
    def __init__(self):
        self.shards = defaultdict(list)
        self.invalid_shard_handler = lambda helper_class, shard: self.__default_invalid_shard_handler(helper_class,
                                                                                                      shard)

    def __default_invalid_shard_handler(self, helper_class, shard):
        print(f"Shard {shard} has not been registered for helper {helper_class.__name__}", file=sys.stderr)
        sys.exit(5)

    def register_shard(self, helper_class, shard):
        helper_shards = self.shards[helper_class.__name__]
        if shard not in helper_shards:
            helper_shards.append(shard)

    def registered_shards(self, helper_class):
        return self.shards[helper_class.__name__]

    def validate_shard(self, helper_class, shard):
        if shard not in self.registered_shards(helper_class):
            self.invalid_shard_handler(helper_class, shard)

    def set_invalid_shard_handler(self, invalid_shard_handler):
        self.invalid_shard_handler = invalid_shard_handler


@lru_cache
def get_shard_registry():
    return ShardRegistry()


class EnvRegistry:
    def __init__(self):
        self.known_params = defaultdict(int)

    def register_env(self, env_name):
        self.known_params[env_name] += 1
        
    def get_known_env_params(self):
        env_param_list = list(self.known_params.keys())
        env_param_list.sort()
        return env_param_list

    def display(self):
        print()
        print(f"Known Environment Variables: {' '.join(self.get_known_env_params())}")
        print()
        sys.exit(0)


@lru_cache
def get_environment_registry():
    return EnvRegistry()

@lru_cache
def get_known_parsers():
    return {}

def add_env_parser_options(parser: ArgumentParser):
    known_parsers = get_known_parsers()
    if parser not in known_parsers:
        parser.add_argument('-e', '--environment', default=False, action='store_true', 
        help="Displays the known ENVIRONMENT variables that are used as default parser options.")
        known_parsers[parser] = True

def handle_env_display(args):
    if 'environment' in args and args.environment:
        get_environment_registry().display()


def boolify(value):
    result = True
    if value.strip().lower() == "false":
        result = False
    return result

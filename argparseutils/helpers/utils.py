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
import logging
import os
import sys
from collections import defaultdict
from functools import lru_cache
from io import StringIO
from typing import Any
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def __get_env__(var_name: str, default: object = None, type: type = str, shard: str = "") -> object:
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
        return True, type(os.environ[var_name])
    elif default is not None:
        return True, type(default)

    return False, None


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


class APUHelpFormatter(ArgumentDefaultsHelpFormatter):

    def display_env_args(self, *args):
        return get_environment_registry().get_help()

    def format_help(self):
        self._root_section.items.append((lambda *args: self.display_env_args(*args), []))
        help = super().format_help()
        return help


def fix_formatter_class(parser, formatter=APUHelpFormatter):
    if not isinstance(parser.formatter_class, APUHelpFormatter):
        parser.formatter_class = APUHelpFormatter
    add_helper_logger(parser)


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

    def display(self, prefix="", stream=sys.stdout, call_exit=True):
        print(f"{prefix}Known Environment Variables: {' '.join(self.get_known_env_params())}", file=stream)
        print(file=stream)
        if call_exit:
            sys.exit(0)

    def get_help(self):
        stream = StringIO()
        print("environment variables:", file=stream)
        self.display(prefix='\t', stream=stream, call_exit=False)
        return stream.getvalue()


@lru_cache
def get_environment_registry():
    return EnvRegistry()

@lru_cache
def get_known_parsers():
    return {}

def add_helper_logger(parser):
    if not hasattr(parser, 'logger'):
        logger = logging.getLogger("APH")
        setattr(parser, 'logger', logger)

# def add_env_parser_options(parser: ArgumentParser):
    # known_parsers = get_known_parsers()
    # if parser not in known_parsers:
    #     parser.add_argument('-e', '--environment', default=False, action='store_true',
    #     help="Displays the known ENVIRONMENT variables that are used as default parser options.")
    #     known_parsers[parser] = True
    # add_helper_logger(parser)

# def handle_env_display(args):
    # if 'environment' in args and args.environment:
    #     get_environment_registry().display()


def boolify(value):
    if type(value) == bool:
        return value
    result = True
    if value.strip().lower() == "false":
        result = False
    return result

def convert_name(name: str) -> str:
    return name.replace("-", "_")

def get_env_name(name: str) -> str:
    return convert_name(name).upper()

def add_option(parser: ArgumentParser, user_kwargs, **kwargs ):
    shard = kwargs.get("shard", "")
    cli_shard, help_shard = get_shard_values(shard)
    is_shard = len(shard.strip()) > 0
    is_required = False

    opt_args = []
    opt_kwargs = {}
    name = None
    if 'short' in kwargs:
        if not is_shard:
            opt_args.append(f"-{kwargs['short']}")
        else:
            parser.logger.warning(f"Ignoring short {kwargs['short']}, due to sharding")

    if 'name' in kwargs:
        name = kwargs['name']
        opt_args.append(f"--{cli_shard}{kwargs['name']}")
    else:
        raise Exception("add_option function expected a name kwarg")
    if 'required' in kwargs:
        opt_kwargs['required'] = kwargs['required']
        is_required = True
    if 'help' in kwargs:
        opt_kwargs['help'] = f"{kwargs['help']}. {help_shard}"
    if 'choices' in kwargs:
        opt_kwargs['choices'] = kwargs['choices']
    if 'type' in kwargs:
        opt_kwargs['type'] = kwargs['type']

    has_author_default_default = False
    author_default = None
    if 'author_default' in kwargs:
        author_default = kwargs['author_default']
        has_author_default_default = True

    has_user_default = False
    user_default = None
    if name in user_kwargs:
        has_user_default = True
        user_default = user_kwargs[name]
    elif convert_name(name) in user_kwargs:
        has_user_default = True
        user_default = user_kwargs[convert_name(name)]

    genv = dict(shard=shard)
    if has_author_default_default:
        genv['default'] = author_default

    if has_user_default:
        genv['default'] = user_default

    if 'type' in kwargs:
        genv['type'] = kwargs['type']


    has_default, default =__get_env__(get_env_name(name), **genv)

    if has_default:
        opt_kwargs['default'] = default

        # If the option is required, and we have loaded a default from the environment
        # we do not need to enforce required.
        if is_required:
            opt_kwargs['required'] = False


    parser.add_argument(*opt_args, **opt_kwargs)





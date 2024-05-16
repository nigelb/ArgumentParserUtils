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


def __get_env__(var_name: str, default: object, type: type = str, env=None) -> object:
    """
    __get_env__ Looks up the value of the field `var_name` firstly in `env` secondly in the environmental
    variables then if`var_name` it is still not found returns the `default` value

    :param var_name: The variable to lookup in `env` and the in the environmental variables
    :param default: If the `var_name` variable is not found, return this value
    :param type: The type to convert the found value to
    :param env: The dictionary to look for `var_name` in
    :return: The found value or `default`
    """
    if env is not None and var_name in env:
        return type(env[var_name].value)
    elif var_name in os.environ:
        return type(os.environ[var_name])
    elif default is not None:
        return type(default)

    return None

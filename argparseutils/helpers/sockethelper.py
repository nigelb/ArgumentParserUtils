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

import os
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from argparseutils.helpers.utils import fix_formatter_class, get_args, \
    get_shard_registry, add_env_parser_options, handle_env_display, boolify, add_option

@dataclass
class SocketConfig:
    address: str
    port: int


class SocketHelper:

    @classmethod
    def add_parser_options(cls, parser: ArgumentParser, shard:str="http", **kwargs):

        fix_formatter_class(parser)
        get_shard_registry().register_shard(cls, shard)
        add_env_parser_options(parser)
        add_option(parser, kwargs, name="address", author_default="0.0.0.0", shard=shard,
                   help="The IP address to bind to")
        add_option(parser, kwargs, name="port", author_default=8080, typ=int, shard=shard,
                   help="The port address to bind to")

    @classmethod
    def get_socket_config(cls, args, shard="http"):
        shard_args = get_args(args, shard)
        return SocketConfig(address=shard_args.address, port=shard_args.port)

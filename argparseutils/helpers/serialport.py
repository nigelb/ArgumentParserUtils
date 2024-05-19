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
from decimal import Decimal

from serial import Serial
from serial.serialutil import FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS, PARITY_NONE, PARITY_EVEN, PARITY_ODD, \
    PARITY_MARK, PARITY_SPACE, STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO

from argparseutils.helpers.utils import get_shard_values, __get_env__, fix_formatter_class, get_args, get_shard_registry


class SerialHelper:
    parity_map = {
        "None": PARITY_NONE,
        "Even": PARITY_EVEN,
        "Odd": PARITY_ODD,
        "Mark": PARITY_MARK,
        "Space": PARITY_SPACE
    }

    @classmethod
    def add_parser_options(cls, parser, shard=""):
        cli_shard, help_shard = get_shard_values(shard)
        fix_formatter_class(parser)
        get_shard_registry().register_shard(cls, shard)

        parser.add_argument(f"--{cli_shard}port", default=__get_env__("PORT", "localhost", shard=shard),
                            help=f"The Serial port to connect to. {help_shard}")
        parser.add_argument(f"--{cli_shard}baudrate", default=__get_env__("baudrate", 9600, shard=shard), type=int,
                            help=f"The Serial port baudrate to use. {help_shard}")
        parser.add_argument(f"--{cli_shard}bytesize", default=__get_env__("bytesize", EIGHTBITS, shard=shard),
                            choices=[FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS], type=int,
                            help=f"The number of bits for each byte. {help_shard}")
        parser.add_argument(f"--{cli_shard}parity", default=__get_env__("parity", "None", shard=shard),
                            choices=cls.parity_map.keys(), help=f"The parity algorithm to use. {help_shard}")
        parser.add_argument(f"--{cli_shard}stopbits", default=__get_env__("stopbits", STOPBITS_ONE, shard=shard),
                            choices=[STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO], type=Decimal,
                            help=f"The number of stop bits to use. {help_shard}")
        parser.add_argument(f"--{cli_shard}timeout", default=__get_env__("timeout", None, shard=shard), type=Decimal,
                            help=f"The read timeout to use (seconds). {help_shard}")
        parser.add_argument(f"--{cli_shard}xonxoff", default=__get_env__("xonxoff", False, shard=shard), type=bool,
                            choices=[True, False], help=f"Use software flow control. {help_shard}")
        parser.add_argument(f"--{cli_shard}rtscts", default=__get_env__("rtscts", False, shard=shard), type=bool,
                            choices=[True, False], help=f"Use RTS/CTS hardware flow control. {help_shard}")
        parser.add_argument(f"--{cli_shard}write-"
                            f"timeout", default=__get_env__("write_timeout", None, shard=shard),
                            type=Decimal, help=f"The write timeout to use (seconds). {help_shard}")
        parser.add_argument(f"--{cli_shard}dsrdtr", default=__get_env__("dsrdtr", False, shard=shard), type=bool,
                            choices=[True, False], help=f"Use DSR/DTR hardware flow control. {help_shard}")
        parser.add_argument(f"--{cli_shard}inter_byte_timeout",
                            default=__get_env__("inter-byte-timeout", None, shard=shard), type=Decimal,
                            help=f"The inter byte timeout to use. Disabled by default. {help_shard}")

        if os.name == 'posix':
            parser.add_argument(f"--{cli_shard}exclusive", default=__get_env__("exclusive", None, shard=shard),
                                type=bool, choices=[True, False],
                                help=f"Open the serial port in exclusive mode. {help_shard}")

    @classmethod
    def validate_args(cls, args, shard=""):
        return True

    @classmethod
    def create_serial(cls, args, shard=""):
        get_shard_registry().validate_shard(cls, shard)

        args = get_args(args, shard)
        kwargs = dict(
            port=args.port,
            bytesize=args.bytesize,
            parity=cls.parity_map[args.parity],
            stopbits=args.stopbits,
            timeout=args.timeout,
            xonxoff=args.xonxoff,
            rtscts=args.rtscts,
            write_timeout=args.write_timeout,
            dsrdtr=args.dsrdtr,
            inter_byte_timeout=args.inter_byte_timeout,
        )
        if os.name == 'posix':
            kwargs['exclusive'] = args.exclusive,

        port = Serial(**kwargs)
        port.args = args
        return port


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser("Serial Test")
    SerialHelper.add_parser_options(parser, "input")

    args = parser.parse_args()
    input_port = SerialHelper.create_serial(args, "input")

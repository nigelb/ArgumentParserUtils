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
from serial.tools import list_ports
from serial.serialutil import FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS, PARITY_NONE, PARITY_EVEN, PARITY_ODD, \
    PARITY_MARK, PARITY_SPACE, STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO

from argparseutils.helpers.utils import get_shard_values, __get_env__, fix_formatter_class, get_args, \
    get_shard_registry, add_env_parser_options, handle_env_display


class SerialHelper:
    parity_map = {
        "None": PARITY_NONE,
        "Even": PARITY_EVEN,
        "Odd": PARITY_ODD,
        "Mark": PARITY_MARK,
        "Space": PARITY_SPACE
    }

    stopbit_map = {
        str(STOPBITS_ONE): STOPBITS_ONE,
        str(STOPBITS_ONE_POINT_FIVE): STOPBITS_ONE_POINT_FIVE,
        str(STOPBITS_TWO): STOPBITS_TWO
    }

    @classmethod
    def add_parser_options(cls, parser, shard="", **kwargs):
        cli_shard, help_shard = get_shard_values(shard)
        fix_formatter_class(parser)
        get_shard_registry().register_shard(cls, shard)
        add_env_parser_options(parser)

        parser.add_argument(f"--{cli_shard}port", 
                            default=__get_env__("PORT", kwargs.get("port", list_ports.comports()[0].device), shard=shard),
                            help=f"The Serial port to connect to. {help_shard}")
        parser.add_argument(f"--{cli_shard}baudrate", default=__get_env__("BAUDRATE", kwargs.get("baudrate", 9600), shard=shard), type=int,
                            help=f"The Serial port baudrate to use. {help_shard}")
        parser.add_argument(f"--{cli_shard}bytesize", default=__get_env__("BYTESIZE", kwargs.get("bytesize", EIGHTBITS), shard=shard),
                            choices=[FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS], type=int,
                            help=f"The number of bits for each byte. {help_shard}")
        parser.add_argument(f"--{cli_shard}parity", default=__get_env__("PARITY", kwargs.get("parity", "None"), shard=shard),
                            choices=cls.parity_map.keys(), help=f"The parity algorithm to use. {help_shard}")
        parser.add_argument(f"--{cli_shard}stopbits", default=__get_env__("STOPBITS", kwargs.get("stopbits", str(STOPBITS_ONE)), shard=shard),
                            choices=cls.stopbit_map.keys(),
                            help=f"The number of stop bits to use. {help_shard}")
        parser.add_argument(f"--{cli_shard}timeout", default=__get_env__("TIMEOUT", kwargs.get("timeout", None), shard=shard), type=Decimal,
                            help=f"The read timeout to use (seconds). {help_shard}")
        parser.add_argument(f"--{cli_shard}xonxoff", default=__get_env__("XONXOFF", kwargs.get("xonxoff", False), shard=shard), type=bool,
                            choices=[True, False], help=f"Use software flow control. {help_shard}")
        parser.add_argument(f"--{cli_shard}rtscts", default=__get_env__("RTSCTS", kwargs.get("rtscts", False), shard=shard), type=bool,
                            choices=[True, False], help=f"Use RTS/CTS hardware flow control. {help_shard}")
        parser.add_argument(f"--{cli_shard}write-timeout", default=__get_env__("WRITE_TIMEOUT", kwargs.get("write-timeout", None), shard=shard),
                            type=Decimal, help=f"The write timeout to use (seconds). {help_shard}")
        parser.add_argument(f"--{cli_shard}dsrdtr", default=__get_env__("DSRDTR", kwargs.get("dsrdtr", False), shard=shard), type=bool,
                            choices=[True, False], help=f"Use DSR/DTR hardware flow control. {help_shard}")
        parser.add_argument(f"--{cli_shard}inter_byte_timeout",
                            default=__get_env__("INTER_BYTE_TIMEOUT", kwargs.get("inter_byte_timeout", None), shard=shard), type=Decimal,
                            help=f"The inter byte timeout to use. Disabled by default. {help_shard}")

        if os.name == 'posix':
            parser.add_argument(f"--{cli_shard}exclusive", default=__get_env__("EXCLUSIVE", kwargs.get("exclusive", None), shard=shard),
                                type=bool, choices=[True, False],
                                help=f"Open the serial port in exclusive mode. {help_shard}")

    @classmethod
    def validate_args(cls, args, shard=""):
        handle_env_display(args)
        return True

    @classmethod
    def create_serial_kwargs(cls, args, shard=""):
        get_shard_registry().validate_shard(cls, shard)

        args = get_args(args, shard)
        kwargs = dict(
            port=args.port,
            baudrate=args.baudrate,
            bytesize=args.bytesize,
            parity=cls.parity_map[args.parity],
            stopbits=cls.stopbit_map[args.stopbits],
            xonxoff=args.xonxoff,
            rtscts=args.rtscts,
            dsrdtr=args.dsrdtr,
        )

        if args.timeout is not None:
            kwargs['timeout'] = args.timeout

        if args.write_timeout is not None:
            kwargs['write_timeout'] = args.write_timeout

        if args.inter_byte_timeout is not None:
            kwargs['inter_byte_timeout'] = args.inter_byte_timeout

        if os.name == 'posix':
            if args.exclusive is not None:
                kwargs['exclusive'] = args.exclusive
        
        return kwargs

    
    @classmethod
    def create_serial(cls, args, shard=""):
        handle_env_display(args)
        port = Serial(**cls.create_serial_kwargs(args, shard))
        port.args = args
        return port


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser("Serial Test")
    SerialHelper.add_parser_options(parser, "input")

    args = parser.parse_args()
    input_port = SerialHelper.create_serial(args, "input")

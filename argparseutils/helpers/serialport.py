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


from serial import Serial
from serial.tools import list_ports
from serial.serialutil import FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS, PARITY_NONE, PARITY_EVEN, PARITY_ODD, \
    PARITY_MARK, PARITY_SPACE, STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO

from argparseutils.helpers.utils import fix_formatter_class, get_args, \
    get_shard_registry, boolify, add_option


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
    def add_parser_options(cls, parser: ArgumentParser, shard:str="", **kwargs):

        fix_formatter_class(parser)
        get_shard_registry().register_shard(cls, shard)

        default_port = None
        known_ports = list_ports.comports()
        if len(known_ports) > 0:
            default_port = known_ports[0].device

        add_option(parser, kwargs, name='port', author_default=default_port, shard=shard, required=default_port is None,
                             help="The Serial port to connect to")

        add_option(parser, kwargs, name="baudrate", author_default=9600, shard=shard,
                   help="The Serial port baudrate to use")

        add_option(parser, kwargs, name="bytesize", author_default=EIGHTBITS, shard=shard,
                   choices=[FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS], type=int, help="The number of bits for each byte")

        add_option(parser, kwargs, name="parity", author_default="None", shard=shard, choices=cls.parity_map.keys(),
                   help="The parity algorithm to use")

        add_option(parser, kwargs, name="stopbits", author_default=str(STOPBITS_ONE), shard=shard, choices=cls.stopbit_map.keys(),
                   help="The number of stop bits to use")

        add_option(parser, kwargs, name="timeout", author_default=None, shard=shard, type=int,
                   help="The read timeout to use (seconds)")

        add_option(parser, kwargs, name="xonxoff", author_default=False, shard=shard, type=boolify,
                   choices=[True, False], help="Use software flow control")

        add_option(parser, kwargs, name="rtscts", author_default=False, shard=shard, type=boolify,
                   choices=[True, False], help="Use RTS/CTS hardware flow control")

        add_option(parser, kwargs, name="dsrdtr", author_default=False, shard=shard, type=boolify,
                   choices=[True, False], help="Use DSR/DTR hardware flow control")

        add_option(parser, kwargs, name="write-timeout", author_default=None, shard=shard,
                   help="The write timeout to use (seconds)")

        add_option(parser, kwargs, name="inter-byte-timeout", author_default=None, shard=shard,
                   help="The inter byte timeout to use. Disabled by default")

        if os.name == 'posix':
            add_option(parser, kwargs, name="exclusive", author_default=None, shard=shard, type=boolify,
                       choices=[True, False], help="Open the serial port in exclusive mode")

    @classmethod
    def validate_args(cls, args: Namespace, shard=""):
        return True

    @classmethod
    def create_serial_kwargs(cls, args: Namespace, shard: str=""):
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
        port = Serial(**cls.create_serial_kwargs(args, shard))
        port.args = args
        return port


if __name__ == "__main__":

    test_parser = ArgumentParser("SerialHelper Test")
    SerialHelper.add_parser_options(test_parser)

    test_args = test_parser.parse_args()
    input_port = SerialHelper.create_serial(test_args)

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

from argparse import ArgumentParser

from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient
from serial.serialutil import EIGHTBITS, FIVEBITS, SIXBITS, SEVENBITS, STOPBITS_ONE
from serial.tools import list_ports

from argparseutils.helpers.serialport import SerialHelper
from argparseutils.helpers.utils import add_option, fix_formatter_class, add_env_parser_options, handle_env_display, \
    boolify


class ModbusSerialHelper:

    @classmethod
    def add_parser_options(cls, parser, shard="", **kwargs):
        fix_formatter_class(parser)
        add_env_parser_options(parser)

        default_port = None
        known_ports = list_ports.comports()
        if len(known_ports) > 0:
            default_port = known_ports[0].device

        add_option(parser, kwargs, name='modbus-port', author_default=default_port, shard=shard,
                   required=default_port is None, help="The Serial port to connect to")

        add_option(parser, kwargs, name="modbus-framer", author_default=FramerType.RTU.value,
                   choices=[FramerType.RTU.value, FramerType.ASCII.value], help="The modbus framer to use")

        add_option(parser, kwargs, name="modbus-baudrate", author_default=9600, shard=shard, type=int,
                   help="The Serial port baudrate to use")

        add_option(parser, kwargs, name="modbus-bytesize", author_default=EIGHTBITS, shard=shard,
                   choices=[FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS], type=int, help="The number of bits for each byte")

        add_option(parser, kwargs, name="modbus-parity", author_default="None", shard=shard,
                   choices=SerialHelper.parity_map.keys(), help="The parity algorithm to use")

        add_option(parser, kwargs, name="modbus-stopbits", author_default=str(STOPBITS_ONE), shard=shard, type=int,
                   choices=SerialHelper.stopbit_map.keys(), help="The number of stop bits to use")

        add_option(parser, kwargs, name="modbus-timeout", author_default=10, shard=shard, type=int,
                   help="The read timeout to use (seconds)")

        add_option(parser, kwargs, name="modbus-handle-local-echo", author_default=False, shard=shard, type=boolify,
                   choices=[True, False], help="Discard local echo from dongle")

        add_option(parser, kwargs, name="modbus-broadcast-enable", author_default=False, shard=shard, type=boolify,
                   choices=[True, False], help="Treat modbus address 0 as a broadcast address")

        add_option(parser, kwargs, name="modbus-reconnect-delay", author_default=0.1, shard=shard, type=float,
                   help="Minimum delay in seconds.milliseconds before reconnection")

        add_option(parser, kwargs, name="modbus-max-reconnect-delay", author_default=300, shard=shard, type=float,
                   help="Maximum delay in seconds.milliseconds before reconnection")

        add_option(parser, kwargs, name="modbus-retries", author_default=3, shard=shard, type=float,
                   help="Maximum delay in seconds.milliseconds before reconnection")

    @classmethod
    def validate_args(cls, args):
        handle_env_display(args)
        return True

    @classmethod
    def create_modbus_serial(cls, args):
        handle_env_display(args)
        args.modbus_parity = SerialHelper.parity_map[args.modbus_parity]
        kwargs = dict(
            port=args.modbus_port,
            framer=FramerType(args.modbus_framer),
            baudrate=args.modbus_baudrate,
            bytesize=args.modbus_bytesize,
            parity=args.modbus_parity,
            stopbits=args.modbus_stopbits,
            timeout=args.modbus_timeout,
            handle_local_echo=args.modbus_handle_local_echo,
            reconnect_delay=args.modbus_reconnect_delay,
            reconnect_delay_max=args.modbus_max_reconnect_delay,
            retries=args.modbus_retries,

        )

        port = ModbusSerialClient(**kwargs)
        port.args = args
        return port


if __name__ == '__main__':
    parser = ArgumentParser("ModbusSerialHelper_Example")

    ModbusSerialHelper.add_parser_options(parser)

    args = parser.parse_args()

    mb_client = ModbusSerialHelper.create_modbus_serial(args)


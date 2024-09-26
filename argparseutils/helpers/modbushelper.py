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
from decimal import Decimal

from argparseutils.helpers.utils import __get_env__, fix_formatter_class, get_shard_registry, get_shard_values, \
    add_env_parser_options, handle_env_display
from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient
from serial.serialutil import EIGHTBITS, FIVEBITS, SIXBITS, SEVENBITS, STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, \
    STOPBITS_TWO, PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE

parity_map = {
    "None": PARITY_NONE,
    "Even": PARITY_EVEN,
    "Odd": PARITY_ODD,
    "Mark": PARITY_MARK,
    "Space": PARITY_SPACE
}


class ModbusSerialHelper:

    @classmethod
    def add_parser_options(cls, parser):
        fix_formatter_class(parser)
        add_env_parser_options(parser)

        parser.add_argument("--port", default=__get_env__("MODBUS_PORT", "/dev/ttyUSB0"),
                            help="The Serial port to connect to.")

        parser.add_argument("--framer", choices=[FramerType.RTU.value, FramerType.ASCII.value],
                            default=__get_env__("MODBUS_FRAMER", FramerType.RTU.value), type=str,
                            help="The modbus framer to use.")

        parser.add_argument("--baudrate", default=__get_env__("MODBUS_BAUDRATE", 9600), type=int,
                            help="The Serial port baud rate to use.")

        parser.add_argument("--bytesize", default=__get_env__("MODBUS_BYTESIZE", EIGHTBITS),
                            choices=[FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS], type=int,
                            help="The number of bits for each byte.")

        parser.add_argument("--parity", default=__get_env__("MODBUS_PARITY", "None"),
                            choices=parity_map.keys(), help=f"The parity algorithm to use.")

        parser.add_argument("--stopbits", default=__get_env__("MODBUS_STOPBITS", STOPBITS_ONE),
                            choices=[STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO], type=Decimal,
                            help="The number of stop bits to use.")

        parser.add_argument("--timeout", default=__get_env__("MODBUS_TIMEOUT", 10), type=float,
                            help="The read timeout to use (seconds).")

        parser.add_argument("--handle-local-echo", action="store_true",
                            default=__get_env__("MODBUS_HANDLE_LOCAL_ECHO", False),
                            help="Discard local echo from dongle.")

        parser.add_argument("--broadcast-enable", action="store_true",
                            default=__get_env__("MODBUS_BROADCAST_ENABLE", False),
                            help="Treat modbus address 0 as a broadcast address.")

        parser.add_argument("--reconnect-delay", default=__get_env__("MODBUS_RECONNECT_DELAY", 0.1), type=float,
                            help="Minimum delay in seconds.milliseconds before reconnection")

        parser.add_argument("--max-reconnect-delay", default=__get_env__("MODBUS_MAX_RECONNECT_DELAY", 300.0),
                            type=float,
                            help="Maximum delay in seconds.milliseconds before reconnection")

        parser.add_argument("--retries", default=__get_env__("MODBUS_RETRIES", 3),
                            type=float,
                            help="Maximum delay in seconds.milliseconds before reconnection")

    @classmethod
    def validate_args(cls, args):
        handle_env_display(args)
        return True

    @classmethod
    def create_modbus_serial(cls, args):
        handle_env_display(args)
        kwargs = dict(
            port=args.port,
            framer=FramerType(args.framer),
            baudrate=args.baudrate,
            bytesize=args.bytesize,
            parity=args.parity,
            stopbits=args.stopbits,
            timeout=args.timeout,
            handle_local_echo=args.handle_local_echo,
            reconnect_delay=args.reconnect_delay,
            reconnect_delay_max=args.max_reconnect_delay,
            retries=args.retries,

        )

        port = ModbusSerialClient(**kwargs)
        port.args = args
        return port


if __name__ == '__main__':

    parser = ArgumentParser("ModbusSerialHelper_Example")

    ModbusSerialHelper.add_parser_options(parser)

    args = parser.parse_args()

    mb_client = ModbusSerialHelper.create_modbus_serial(args)


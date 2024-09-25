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

import ssl

import paho.mqtt.client as mqtt_client
from paho.mqtt.enums import CallbackAPIVersion

from argparseutils.helpers.utils import CliShardWrapper, __get_env__, get_shard_values, fix_formatter_class, get_args, \
    get_shard_registry, add_env_parser_options, handle_env_display


class MQTTClientHelper:

    @classmethod
    def add_parser_options(cls, parser, mqtt_client_id, shard=""):
        cli_shard, help_shard = get_shard_values(shard)
        fix_formatter_class(parser)
        get_shard_registry().register_shard(cls, shard)
        add_env_parser_options(parser)

        parser.add_argument("--%smqtt-host" % cli_shard, default=__get_env__("MQTT_HOST", "localhost", shard=shard),
                            help="The MQTT server hostname to connect to%s." % help_shard)
        parser.add_argument("--%smqtt-port" % cli_shard, default=__get_env__("MQTT_PORT", 1883, type=int, shard=shard),
                            type=int, help="The MQTT Server port on connect to%s." % help_shard)
        parser.add_argument("--%smqtt-ssl" % cli_shard, action="store_true",
                            help="Use SSL when connecting to the MQTT server%s." % help_shard)
        parser.add_argument("--%smqtt-client-id" % cli_shard,
                            default=__get_env__("MQTT_CLIENT_ID", mqtt_client_id, shard=shard),
                            help="The MQTT Client Id to use on the connection%s." % help_shard)
        parser.add_argument("--%smqtt-keepalive" % cli_shard,
                            default=__get_env__("MQTT_KEEPALIVE", 60, type=int, shard=shard), type=int,
                            help="The MQTT connection keepalive%s." % help_shard)
        parser.add_argument("--%smqtt-username" % cli_shard, default=__get_env__("MQTT_USERNAME", None, shard=shard),
                            help="The MQTT Username to connect with%s." % help_shard)
        parser.add_argument("--%smqtt-password" % cli_shard, default=__get_env__("MQTT_PASSWORD", None, shard=shard),
                            help="The MQTT Password to connect with%s." % help_shard)
        parser.add_argument("--%smqtt-transport" % cli_shard, default=__get_env__("MQTT_TRANSPORT", 'tcp', shard=shard),
                            choices=['tcp', 'websockets'],
                            help="The MQTT Transport to use with the connection%s." % help_shard)
        parser.add_argument("--%smqtt-clean-session" % cli_shard, default=__get_env__("MQTT_CLEAN_SESSION", True, shard=shard), type=bool,
                            help="If False, the client is a persistent client and subscription information and queued " \
                                 "messages will be retained when the client disconnects%s." % help_shard)
        parser.add_argument("--%smqtt-ws-path" % cli_shard, default=__get_env__("MQTT_WS_PATH", '/mqtt/', shard=shard),
                            help="The MQTT Websocket path%s." % help_shard)

    @classmethod
    def validate_args(cls, args, shard=""):
        handle_env_display(args)
        return True

    @classmethod
    def create_client(cls, args, shard=""):
        handle_env_display(args)
        args = get_args(args, shard)

        client = mqtt_client.Client(
            client_id=args.mqtt_client_id,
            clean_session=args.mqtt_clean_session,
            transport=args.mqtt_transport,
            callback_api_version=CallbackAPIVersion.VERSION2
        )
        client.args = args
        client.ws_set_options(path=args.mqtt_ws_path)
        if args.mqtt_ssl:
            client.tls_set(
                ca_certs=None,
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None)

        if args.mqtt_username is not None:
            client.username_pw_set(args.mqtt_username, args.mqtt_password)

        return client

    @classmethod
    def connect(cls, client):
        args = client.args
        client.connect(args.mqtt_host, port=args.mqtt_port, keepalive=args.mqtt_keepalive)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser("MQTT Test")
    MQTTClientHelper.add_parser_options(parser, "test", shard="input")

    args = parser.parse_args()
    input_port = MQTTClientHelper.create_client(args, shard="input")

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

from argparseutils.helpers.utils import add_option, boolify, fix_formatter_class, get_args, \
    get_shard_registry, add_env_parser_options, handle_env_display


class MQTTClientHelper:

    @classmethod
    def add_parser_options(cls, parser, mqtt_client_id, shard="", **kwargs):

        fix_formatter_class(parser)
        get_shard_registry().register_shard(cls, shard)
        add_env_parser_options(parser)

        add_option(parser, kwargs, name="mqtt-host", author_default="localhost", shard=shard,
                   help="The MQTT server hostname to connect to")

        add_option(parser, kwargs, name="mqtt-port", author_default=1883, shard=shard, type=int,
                   help="The MQTT Server port on connect to")

        add_option(parser, kwargs, name="mqtt-ssl", author_default=False, shard=shard, type=boolify,
                   choices=[True, False], help="Use SSL when connecting to the MQTT server")

        add_option(parser, kwargs, name="mqtt-client-id", author_default=mqtt_client_id, shard=shard,
                   help="The MQTT Client Id to use on the connection")

        add_option(parser, kwargs, name="mqtt-keepalive", author_default=60, shard=shard, type=int,
                   help="The MQTT connection keepalive")

        add_option(parser, kwargs, name="mqtt-username", author_default=None, shard=shard,
                   help="The MQTT Username to connect with")

        add_option(parser, kwargs, name="mqtt-password", author_default=None, shard=shard,
                   help="The MQTT Password to connect with")

        add_option(parser, kwargs, name="mqtt-transport", author_default="tcp", shard=shard,
                   choices=['tcp', 'websockets'], help="The MQTT Transport to use with the connection")

        add_option(parser, kwargs, name="mqtt-clean-session", author_default=True, shard=shard, type=boolify,
                   choices=[True, False],
                   help="If False, the client is a persistent client and subscription information and queued " \
                                 "messages will be retained when the client disconnects")

        add_option(parser, kwargs, name="mqtt-ws-path", author_default="/mqtt/", shard=shard,
                   help="The MQTT Websocket path")

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

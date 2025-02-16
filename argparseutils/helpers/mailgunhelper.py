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
import logging
from argparse import ArgumentParser
from typing import List

import requests

from argparseutils.helpers.util.email import EmailAddress, EmailClient, EmailStatus
from argparseutils.helpers.utils import fix_formatter_class, add_option, get_args



class MailgunClient(EmailClient):
    logger = logging.getLogger("MailgunClient")
    def __init__(self, api_key, domain):
        self.api_key = api_key
        self.domain = domain

    def send_simple_message(self, to: List[EmailAddress], sender: EmailAddress, subject: str, body: str):
        data = {"from": str(sender),
                "to": [str(x) for x in to],
                "subject": subject,
                "text": body}
        self.logger.debug(f'Sending email: {data}')
        result = requests.post(
            f"https://api.mailgun.net/v3/{self.domain}/messages",
            auth=("api", self.api_key),
            data=data)
        self.logger.info(f'Email to: {to}, subject: {subject}, sent: {result.status_code == 200}')
        return EmailStatus(result.status_code == 200, result.json())

class MailGunHelper:
    @classmethod
    def add_parser_options(cls, parser: ArgumentParser, shard="", **user_defaults):
        fix_formatter_class(parser)
        add_option(parser, user_defaults, name="mailgun-api-key", shard=shard, required=True,
                   help="The Mailgun API Key to use")
        add_option(parser, user_defaults, name="mailgun-domain", shard=shard, required=True,
                   help="The Mailgun domain to use")

    @classmethod
    def create_client(cls, args, shard=""):
        args = get_args(args, shard)

        client = MailgunClient(args.mailgun_api_key, args.mailgun_domain)
        client.args = args
        return client

def main():
    parser = ArgumentParser("Mailgun")
    MailGunHelper.add_parser_options(parser)
    parser.add_argument("--to", action="append", default=[], type=EmailAddress.from_address, help="The email address to send to", required=True)
    parser.add_argument("--sender", type=EmailAddress.from_address, help="The email address to send from", required=True)
    parser.add_argument("--subject", type=str, help="The subject of the email", required=True)
    parser.add_argument("--body", type=str, help="The body of the email", required=True)

    args = parser.parse_args()

    client = MailGunHelper.create_client(args)
    result = client.send_simple_message(args.to, args.sender, args.subject, args.body)
    print(result)


if __name__ == '__main__':
    main()
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
from dataclasses import dataclass
from email import utils
from typing import List, Any


class EmailAddress:
    def __init__(self, real_name: str|None, address: str) -> None:
        self.real_name = real_name
        self.address = address

    def __str__(self):
        if self.real_name is None:
            return self.address
        return f'{self.real_name} <{self.address}>'

    @classmethod
    def from_address(cls, to_parse: str) -> 'EmailAddress':
        real_name, address = utils.parseaddr(to_parse)
        if len(real_name.strip()) == 0:
            real_name = None
        return EmailAddress(real_name, address)

@dataclass
class EmailStatus:
    sent: bool
    result: Any

class EmailClient:
    def send_simple_message(self, to: List[EmailAddress], sender: EmailAddress, subject: str, body: str) -> EmailStatus:
        raise NotImplementedError("send_simple_message not implemented")
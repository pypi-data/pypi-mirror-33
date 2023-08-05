#   Copyright 2018 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
    Deserialized representation of the firmware command sent from the platform
"""


class FirmwareCommand:
    """
        Firmware Command
    """

    def __init__(
        self,
        command,
        file_name=None,
        file_size=None,
        file_hash=None,
        auto_install=None,
        file_url=None,
    ):
        """
        :param command: The command to be executed
        :type command: FirmwareCommandType
        :param file_name: The name of the file to be received
        :type file_name: string
        :param file_size: The size of the file to be received
        :type file_size: int
        :param file_hash: The hash of the file to be received
        :type file_hash: string
        :param auto_install: Install the file when it is received
        :type auto_install: Boolean
        :param file_url: The URL where the file is located
        :type file_url: string
        """
        self.command = command
        self.file_name = file_name
        self.file_size = file_size
        self.file_hash = file_hash
        self.auto_install = auto_install
        self.file_url = file_url

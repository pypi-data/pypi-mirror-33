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
    Deserialized representation of the actuator command sent from the platform
"""


class ActuatorCommand:
    """
        Actuator Command
    """

    def __init__(self, reference, command, value=None):
        """
        :param reference: The reference of the actuator
        :type reference: str
        :param command: The command to be executed
        :type command: ActuatorCommandType
        :param value: The value to be set to
        :type value: int, string
        """
        self.reference = reference
        self.command = command
        self.value = value

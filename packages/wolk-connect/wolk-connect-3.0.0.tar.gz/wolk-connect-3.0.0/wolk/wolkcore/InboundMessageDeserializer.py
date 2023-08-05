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
    Deserialize the messages received from the platform
"""


class InboundMessageDeserializer:
    """
        Inbound Message Deserializer Interface
    """

    def deserialize_actuator_command(self, message):
        """
        Deserialize the message into an ActuatorCommand

        :param message: The message received
        :type message: InboundMessage
        :returns: actuation
        :rtype: ActuatorCommand
        """
        pass

    def deserialize_firmware_command(self, message):
        """
        Deserializes the message into a FirmwareCommand

        :param message: The message received
        :type message: InboundMessage
        :returns: firmware_command
        :rtype: FirmwareCommand
        """
        pass

    def deserialize_firmware_chunk(self, message):
        """
        Deserializes the message into a tuple of bytes

        :param message: The message received
        :type message: InboundMessage
        :returns: (previous_hash, chunk, chunk_hash)
        :rtype: (bytes, bytes, bytes)
        """
        pass

    def deserialize_configuration_command(self, message):
        """
        Deserializes the message into a ConfigurationCommand

        :param message: The message received
        :type message: InboundMessage
        :returns: configuration
        :rtype: ConfigurationCommand
        """
        pass

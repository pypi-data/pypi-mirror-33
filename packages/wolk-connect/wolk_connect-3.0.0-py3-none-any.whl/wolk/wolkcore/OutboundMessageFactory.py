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
    Outbound Message Factory should be implemented to serialize messages
    in a format that is expected to be received from the platform.
"""


class OutboundMessageFactory:
    """
        Outbound Message Factory Interface
    """

    def make_from_sensor_reading(self, reading):
        """
        Serializes a sensor reading to be sent to the platform

        :param reading: The reading to be serialized
        :type reading: SensorReading
        :returns: message
        :rtype: OutboundMessage
        """
        pass

    def make_from_alarm(self, alarm):
        """
        Serializes an alarm event to be sent to the platform

        :param alarm: The alarm to be serialized
        :type alarm: Alarm
        :returns: message
        :rtype: OutboundMessage
        """
        pass

    def make_from_actuator_status(self, actuator):
        """
        Serializes an actuator status to be sent to the platform

        :param actuator: The actuator status to be serialized
        :type actuator: ActuatorStatus
        :returns: message
        :rtype: OutboundMessage
        """
        pass

    def make_from_firmware_status(self, firmware_status):
        """
        Reports the current status of the firmware update process

        :param firmware_status: The current status of the firmware update process
        :type firmware_status: FirmwareStatus
        :returns: message
        :rtype: OutboundMessage
        """
        pass

    def make_from_chunk_request(self, file_name, chunk_index, chunk_size):
        """
        Requests a chunk of the firmware file from the platform

        :param file_name: The name of the file that contains the requested chunk
        :type file_name: string
        :param chunk_index: The index of the requested chunk
        :type chunk_index: int
        :param chunk_size: The size of the requested chunk
        :type chunk_size: int
        :returns: message
        :rtype: OutboundMessage
        """
        pass

    def make_from_firmware_version(self, version):
        """
        Reports the current firmware version to the platform

        :param version: Current firmware version
        :type version: str
        :returns: message
        :rtype: OutboundMessage
        """
        pass

    def make_from_keep_alive_message(self):
        """
        Sends a ping to the platform

        :returns: message
        :rtype: OutboundMessage
        """
        pass

    def make_from_configuration(self, configuration):
        """
        Serializes the device's configuration to be sent to the platform

        :param configuration: The device's current configuration
        :type configuration: dict
        :returns: message
        :rtype: OutboundMessage
        """
        pass

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
    Responsible for handling file and URL download, as well as reporting firmware status.
    Should be implemented to depend upon an object of FirmwareHandler class
"""


class FirmwareUpdate:
    """
    Firmware Update class
    """

    def handle_file_download(self, firmware_command):
        """
        Passes the information necessary to start a file download to an instance of FirmwareHandler
        """
        pass

    def handle_url_download(self, firmware_command):
        """
        Passes the information necessary to start a URL download to an instance of FirmwareHandler
        """
        pass

    def handle_url_download_result(self, result):
        """
        Handles the result of the url file download reported from an instance of FirmwareHandler
        """
        pass

    def handle_install(self):
        """
        Passes the install command to an instance of FirmwareHandler
        """
        pass

    def handle_abort(self):
        """
        Passes the abort command to an instance of FirmwareHandler
        """
        pass

    def handle_packet(self, packet):
        """
        Pases the packet to an instance of FirmwareHandler
        """
        pass

    def report_result(self):
        """
        Reports the results of the firmware update process
        """
        pass

    def set_on_file_packet_request_callback(self, on_file_packet_request_callback):
        """
        Sets a callback to handle file packet requests
        """
        pass

    def set_on_status_callback(self, on_status_callback):
        """
        Sets a callback to handle firmware status reporting
        """
        pass

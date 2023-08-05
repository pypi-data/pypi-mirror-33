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
    Implement this class to wire and read files in persistent memory, persist firmware version
    and handle the process of installation of firmware itself.
    Optionally provide implementation for URL download
"""


class FirmwareHandler:
    """
        Firmware Handler Interface
    """

    def update_start(self, file_name, file_size):
        """
        Prepares the device to start the process of firmware update
        """
        pass

    def update_finalize(self):
        """
        Finishes the process of firmware update
        """
        pass

    def update_abort(self):
        """
        Aborts the process of firmware update, returning the device to the idle state
        """
        pass

    def write_chunk(self, chunk):
        """
        Writes the firmware file chunk into persitent memory
        """
        pass

    def read_chunk(self, index):
        """
        Reads the firmware file chunk from persistent memory
        """
        pass

    def persist_version(self, version):
        """
        Places the current firmware version into a persistent queue of messages to be sent to the platform
        """
        pass

    def unpersist_version(self):
        """
        Removed the persisted firmwave version from the queue
        """
        pass

    def update_start_url_download(self, file_url):
        """
        Prepares the device for the URL file transfer
        """
        pass

    def set_url_download_result_callback(self, callback):
        """
        Sets the callback method for reporting the result of URL file download
        """
        pass

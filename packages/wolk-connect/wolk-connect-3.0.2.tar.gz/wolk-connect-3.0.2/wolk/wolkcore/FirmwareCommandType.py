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
    Types of firmware commands received from the platform
"""

FIRMWARE_COMMAND_TYPE_FILE_UPLOAD = 0
FIRMWARE_COMMAND_TYPE_URL_DOWNLOAD = 1
FIRMWARE_COMMAND_TYPE_INSTALL = 2
FIRMWARE_COMMAND_TYPE_ABORT = 3
FIRMWARE_COMMAND_TYPE_UNKNOWN = 4

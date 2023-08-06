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
    This interface will publish messages to the platform in regular intervals to keep device connected in cases
    where no data is being sent for over 30 minutes
"""


class KeepAliveService:
    """
        Keep Alive Service interface
    """

    def handle_pong():
        """
        Currently unused
        """
        pass

    def start():
        """
        Publish a ping message in a repeating interval
        """
        pass

    def stop():
        """
        Stop the repeating interval
        """
        pass

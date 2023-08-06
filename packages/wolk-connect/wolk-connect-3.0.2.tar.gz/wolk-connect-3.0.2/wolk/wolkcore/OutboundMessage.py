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
    Outbound Message that gets published to the platform
"""


class OutboundMessage:
    """
        Outbound Message Class
    """

    def __init__(self, channel, payload):
        """
        :param channel: Defines the channel where the message will be published to
        :type channel: str
        :param payload: Defines the payload of the message that will be published to the channel
        :type payload: str
        """
        self.channel = channel
        self.payload = payload

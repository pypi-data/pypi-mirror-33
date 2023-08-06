# coding: utf-8

#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
#

import pprint
import re  # noqa: F401
import six
import typing
from enum import Enum
from abc import ABCMeta, abstractmethod


if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional
    from datetime import datetime


class Request(object):
    """
    A request object that provides the details of the user’s request. The request body contains the parameters necessary for the service to perform its logic and generate a response.  # noqa: E501

    NOTE: This class is auto generated.
    Do not edit the class manually.

    :param object_type: Describes the type of the request.  # noqa: E501
    :type object_type: (optional) str
    :param request_id: Represents the unique identifier for the specific request.  # noqa: E501
    :type request_id: (optional) str
    :param timestamp: Provides the date and time when Alexa sent the request as an ISO 8601 formatted string. Used to verify the request when hosting your skill as a web service.  # noqa: E501
    :type timestamp: (optional) datetime
    :param locale: A string indicating the user’s locale. For example: en-US.  # noqa: E501
    :type locale: (optional) str
    """
    deserialized_types = {
        'object_type': 'str',
        'request_id': 'str',
        'timestamp': 'datetime',
        'locale': 'str'
    }

    attribute_map = {
        'object_type': 'type',
        'request_id': 'requestId',
        'timestamp': 'timestamp',
        'locale': 'locale'
    }

    discriminator_value_class_map = {
        'AudioPlayer.PlaybackStopped': 'ask_sdk_model.interfaces.audioplayer.playback_stopped_request.PlaybackStoppedRequest',  # noqa: E501
        'AudioPlayer.PlaybackFinished': 'ask_sdk_model.interfaces.audioplayer.playback_finished_request.PlaybackFinishedRequest',  # noqa: E501
        'AlexaSkillEvent.SkillEnabled': 'ask_sdk_model.events.skillevents.skill_enabled_request.SkillEnabledRequest',  # noqa: E501
        'AlexaHouseholdListEvent.ListUpdated': 'ask_sdk_model.services.list_management.list_updated_event_request.ListUpdatedEventRequest',  # noqa: E501
        'PlaybackController.PreviousCommandIssued': 'ask_sdk_model.interfaces.playbackcontroller.previous_command_issued_request.PreviousCommandIssuedRequest',  # noqa: E501
        'AlexaSkillEvent.SkillDisabled': 'ask_sdk_model.events.skillevents.skill_disabled_request.SkillDisabledRequest',  # noqa: E501
        'Display.ElementSelected': 'ask_sdk_model.interfaces.display.element_selected_request.ElementSelectedRequest',  # noqa: E501
        'AlexaHouseholdListEvent.ItemsUpdated': 'ask_sdk_model.services.list_management.list_items_updated_event_request.ListItemsUpdatedEventRequest',  # noqa: E501
        'AlexaSkillEvent.SkillPermissionChanged': 'ask_sdk_model.events.skillevents.permission_changed_request.PermissionChangedRequest',  # noqa: E501
        'AlexaHouseholdListEvent.ItemsCreated': 'ask_sdk_model.services.list_management.list_items_created_event_request.ListItemsCreatedEventRequest',  # noqa: E501
        'AlexaSkillEvent.SkillAccountLinked': 'ask_sdk_model.events.skillevents.account_linked_request.AccountLinkedRequest',  # noqa: E501
        'SessionEndedRequest': 'ask_sdk_model.session_ended_request.SessionEndedRequest',  # noqa: E501
        'AlexaHouseholdListEvent.ListCreated': 'ask_sdk_model.services.list_management.list_created_event_request.ListCreatedEventRequest',  # noqa: E501
        'AudioPlayer.PlaybackStarted': 'ask_sdk_model.interfaces.audioplayer.playback_started_request.PlaybackStartedRequest',  # noqa: E501
        'IntentRequest': 'ask_sdk_model.intent_request.IntentRequest',  # noqa: E501
        'AudioPlayer.PlaybackNearlyFinished': 'ask_sdk_model.interfaces.audioplayer.playback_nearly_finished_request.PlaybackNearlyFinishedRequest',  # noqa: E501
        'AlexaHouseholdListEvent.ItemsDeleted': 'ask_sdk_model.services.list_management.list_items_deleted_event_request.ListItemsDeletedEventRequest',  # noqa: E501
        'Connections.Response': 'ask_sdk_model.interfaces.connections.connections_response.ConnectionsResponse',  # noqa: E501
        'Messaging.MessageReceived': 'ask_sdk_model.interfaces.messaging.message_received_request.MessageReceivedRequest',  # noqa: E501
        'AudioPlayer.PlaybackFailed': 'ask_sdk_model.interfaces.audioplayer.playback_failed_request.PlaybackFailedRequest',  # noqa: E501
        'Connections.Request': 'ask_sdk_model.interfaces.connections.connections_request.ConnectionsRequest',  # noqa: E501
        'System.ExceptionEncountered': 'ask_sdk_model.interfaces.system.exception_encountered_request.ExceptionEncounteredRequest',  # noqa: E501
        'AlexaSkillEvent.SkillPermissionAccepted': 'ask_sdk_model.events.skillevents.permission_accepted_request.PermissionAcceptedRequest',  # noqa: E501
        'AlexaHouseholdListEvent.ListDeleted': 'ask_sdk_model.services.list_management.list_deleted_event_request.ListDeletedEventRequest',  # noqa: E501
        'GameEngine.InputHandlerEvent': 'ask_sdk_model.interfaces.game_engine.input_handler_event_request.InputHandlerEventRequest',  # noqa: E501
        'PlaybackController.NextCommandIssued': 'ask_sdk_model.interfaces.playbackcontroller.next_command_issued_request.NextCommandIssuedRequest',  # noqa: E501
        'PlaybackController.PauseCommandIssued': 'ask_sdk_model.interfaces.playbackcontroller.pause_command_issued_request.PauseCommandIssuedRequest',  # noqa: E501
        'PlaybackController.PlayCommandIssued': 'ask_sdk_model.interfaces.playbackcontroller.play_command_issued_request.PlayCommandIssuedRequest',  # noqa: E501
        'LaunchRequest': 'ask_sdk_model.launch_request.LaunchRequest'
    }

    json_discriminator_key = "type"

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, object_type=None, request_id=None, timestamp=None, locale=None):  # noqa: E501
        # type: (Optional[str], Optional[str], Optional[datetime], Optional[str]) -> None
        """A request object that provides the details of the user’s request. The request body contains the parameters necessary for the service to perform its logic and generate a response.  # noqa: E501

        :param object_type: Describes the type of the request.  # noqa: E501
        :type object_type: (optional) str
        :param request_id: Represents the unique identifier for the specific request.  # noqa: E501
        :type request_id: (optional) str
        :param timestamp: Provides the date and time when Alexa sent the request as an ISO 8601 formatted string. Used to verify the request when hosting your skill as a web service.  # noqa: E501
        :type timestamp: (optional) datetime
        :param locale: A string indicating the user’s locale. For example: en-US.  # noqa: E501
        :type locale: (optional) str
        """
        self.__discriminator_value = None

        self.object_type = object_type
        self.request_id = request_id
        self.timestamp = timestamp
        self.locale = locale

    @classmethod
    def get_real_child_model(cls, data):
        # type: (Dict[str, str]) -> str
        """Returns the real base class specified by the discriminator"""
        discriminator_value = data[cls.json_discriminator_key]
        return cls.discriminator_value_class_map.get(discriminator_value)

    def to_dict(self):
        # type: () -> Dict[str, object]
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.deserialized_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else
                    x.value if isinstance(x, Enum) else x,
                    value
                ))
            elif isinstance(value, Enum):
                result[attr] = value.value
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else
                    (item[0], item[1].value)
                    if isinstance(item[1], Enum) else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        # type: () -> str
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        # type: () -> str
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are equal"""
        if not isinstance(other, Request):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other

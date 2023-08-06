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


class Directive(object):
    """
    NOTE: This class is auto generated.
    Do not edit the class manually.

    :type object_type: (optional) str
    """
    deserialized_types = {
        'object_type': 'str'
    }

    attribute_map = {
        'object_type': 'type'
    }

    discriminator_value_class_map = {
        'VideoApp.Launch': 'ask_sdk_model.interfaces.videoapp.launch_directive.LaunchDirective',  # noqa: E501
        'AudioPlayer.Stop': 'ask_sdk_model.interfaces.audioplayer.stop_directive.StopDirective',  # noqa: E501
        'Dialog.ConfirmSlot': 'ask_sdk_model.dialog.confirm_slot_directive.ConfirmSlotDirective',  # noqa: E501
        'GameEngine.StopInputHandler': 'ask_sdk_model.interfaces.game_engine.stop_input_handler_directive.StopInputHandlerDirective',  # noqa: E501
        'AudioPlayer.Play': 'ask_sdk_model.interfaces.audioplayer.play_directive.PlayDirective',  # noqa: E501
        'Connections.SendResponse': 'ask_sdk_model.interfaces.connections.send_response_directive.SendResponseDirective',  # noqa: E501
        'Connections.SendRequest': 'ask_sdk_model.interfaces.connections.send_request_directive.SendRequestDirective',  # noqa: E501
        'Display.RenderTemplate': 'ask_sdk_model.interfaces.display.render_template_directive.RenderTemplateDirective',  # noqa: E501
        'GadgetController.SetLight': 'ask_sdk_model.interfaces.gadget_controller.set_light_directive.SetLightDirective',  # noqa: E501
        'Dialog.ElicitSlot': 'ask_sdk_model.dialog.elicit_slot_directive.ElicitSlotDirective',  # noqa: E501
        'AudioPlayer.ClearQueue': 'ask_sdk_model.interfaces.audioplayer.clear_queue_directive.ClearQueueDirective',  # noqa: E501
        'Dialog.Delegate': 'ask_sdk_model.dialog.delegate_directive.DelegateDirective',  # noqa: E501
        'Hint': 'ask_sdk_model.interfaces.display.hint_directive.HintDirective',  # noqa: E501
        'Dialog.ConfirmIntent': 'ask_sdk_model.dialog.confirm_intent_directive.ConfirmIntentDirective',  # noqa: E501
        'GameEngine.StartInputHandler': 'ask_sdk_model.interfaces.game_engine.start_input_handler_directive.StartInputHandlerDirective'
    }

    json_discriminator_key = "type"

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, object_type=None):  # noqa: E501
        # type: (Optional[str]) -> None
        """

        :type object_type: (optional) str
        """
        self.__discriminator_value = None

        self.object_type = object_type

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
        if not isinstance(other, Directive):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other

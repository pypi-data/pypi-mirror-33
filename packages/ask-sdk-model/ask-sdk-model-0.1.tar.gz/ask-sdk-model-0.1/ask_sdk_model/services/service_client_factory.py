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

import sys
import os
import re
import six
import typing
from .device_address import DeviceAddressServiceClient
from .directive import DirectiveServiceClient
from .list_management import ListManagementServiceClient
from .monetization import MonetizationServiceClient

if typing.TYPE_CHECKING:
    from .api_configuration import ApiConfiguration


class ServiceClientFactory(object):
    """ServiceClientFactory class to help build service clients."""
    def __init__(self, api_configuration):
        # type: (ApiConfiguration) -> None
        self.api_configuration = api_configuration

    def get_device_address_service(self):
        # type: () -> DeviceAddressServiceClient
        try:
            return DeviceAddressServiceClient(self.api_configuration)
        except Exception as e:
            raise ValueError(
                "ServiceClientFactory Error while initializing DeviceAddressServiceClient: " + e)

    def get_directive_service(self):
        # type: () -> DirectiveServiceClient
        try:
            return DirectiveServiceClient(self.api_configuration)
        except Exception as e:
            raise ValueError(
                "ServiceClientFactory Error while initializing DirectiveServiceClient: " + e)

    def get_list_management_service(self):
        # type: () -> ListManagementServiceClient
        try:
            return ListManagementServiceClient(self.api_configuration)
        except Exception as e:
            raise ValueError(
                "ServiceClientFactory Error while initializing ListManagementServiceClient: " + e)

    def get_monetization_service(self):
        # type: () -> MonetizationServiceClient
        try:
            return MonetizationServiceClient(self.api_configuration)
        except Exception as e:
            raise ValueError(
                "ServiceClientFactory Error while initializing MonetizationServiceClient: " + e)


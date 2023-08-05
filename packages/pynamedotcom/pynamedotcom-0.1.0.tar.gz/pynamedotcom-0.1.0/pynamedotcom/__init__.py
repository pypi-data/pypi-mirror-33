# Copyright (c) 2018 Ben Maddison. All rights reserved.
#
# The contents of this file are licensed under the MIT License
# (the "License"); you may not use this file except in compliance with the
# License.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""pynamedotcom Package."""

from __future__ import print_function
from __future__ import unicode_literals

import logging

import pynamedotcom.__meta__  # noqa
from pynamedotcom.api import API

logging.getLogger(__name__).addHandler(logging.NullHandler())
__all__ = [API.__name__]

#!/usr/bin/env python
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
"""pynamedotcom package metadata."""

from __future__ import print_function
from __future__ import unicode_literals

__version__ = "0.1.1"
__author__ = "Ben Maddison"
__author_email__ = "benm@workonline.co.za"
__licence__ = "MIT"
__copyright__ = "Copyright (c) 2018 Ben Maddison"
__url__ = "https://github.com/benmaddison/pynamedotcom"
__classifiers__ = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet',
]
__entry_points__ = {
    'console_scripts': [
        'namedotcom=pynamedotcom.cli:main',
    ]
}


if __name__ == "__main__":
    print(__version__)

#
# Created on Sun Apr 16 2023
#
# The MIT License (MIT)
# Copyright (c) 2023 silvertoken (https://github.com/silvertoken)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Parameters for routeros modules
    DOCUMENTATION = r'''
notes:
  - All modules requires REST API running on Mikrotik routeros
options:
    hostname:
      description:
      - The hostname or IP address of the router.
      - If the value is not specified in the task, the value of environment variable C(ROUTEROS_HOST) will be used instead.
      type: str
    username:
      description:
      - The username to access the router.
      - If the value is not specified in the task, the value of environment variable C(ROUTEROS_USER) will be used instead.
      type: str
      aliases: [ admin, user ]
    password:
      description:
      - The password of the router.
      - If the value is not specified in the task, the value of environment variable C(ROUTEROS_PASSWORD) will be used instead.
      type: str
      aliases: [ pass, pwd, passwd ]
    validate_certs:
      description:
      - Allows connection when SSL certificates are not valid. Set to C(false) when certificates are not trusted.
      - If the value is not specified in the task, the value of environment variable C(ROUTEROS_VALIDATE_CERTS) will be used instead.
      type: bool
      default: true
    port:
      description:
      - The port number of the router REST api service.
      - If the value is not specified in the task, the value of environment variable C(ROUTEROS_PORT) will be used instead.
      type: int
      default: 443
'''
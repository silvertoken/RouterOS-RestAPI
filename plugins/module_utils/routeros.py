
#
# Created on Sat Apr 15 2023
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

import json
import ssl

from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import open_url

'''Access Error Exceptions'''
class ApiAccessError(Exception):
    def __init__(self, *args, **kwargs):
        super(ApiAccessError, self).__init__(*args, **kwargs)

def routeros_argument_spec():
    return dict(
        hostname=dict(type='str',
                      required=False,
                      fallback=(env_fallback, ['ROUTEROS_HOST']),
        ),
        username=dict(type='str',
                      aliases=['user'],
                      required=False,
                      fallback=(env_fallback, ['ROUTEROS_USER']),
        ),
        password=dict(type='str',
                      aliases=['pass', 'passwd', 'pwd'],
                      required=False,
                      no_log=True,
                      fallback=(env_fallback, ['ROUTEROS_PASSWORD']),
        ),
        port=dict(type='int',
                  default='443',
                  fallback=(env_fallback, ['ROUTEROS_PORT']),
        ),
        validate_certs=dict(type='str',
                      required=False,
                      default=True,
                      fallback=(env_fallback, ['ROUTEROS_VALIDATE_CERTS']),
        ),
    )
    
def request_from_api(module, hostname=None, username=None, password=None, port=None, validate_certs=None, method=None, url=None, payload=None):
    if not hostname:
        hostname = module.params['hostname']
    if not username:
        username = module.params['username']
    if not password:
        password = module.params['password']
    if not port:
        port = module.params.get('port', 443)
    if not validate_certs:
        validate_certs = module.params['validate_certs']
        
    if not method:
        method = 'GET'
    
    '''Standard API Exception'''
    def _raise_or_fail(msg):
        if module is not None:
            module.fail_json(msg=msg)
        raise ApiAccessError(msg)
    
    if not hostname:
        _raise_or_fail(msg="Hostname parameter is missing.")
    if not username:
        _raise_or_fail(msg="Username parameter is missing.")
    if not password:
        _raise_or_fail(msg="Password parameter is missing.")
    if not url:
        _raise_or_fail(msg="Url paramater is missing.")
        
    if validate_certs:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True
        ssl_context.load_default_certs()
    elif hasattr(ssl, 'SSLContext'):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.check_hostname = False
    else:
        ssl_context = None
        
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    rest_url = 'https://' + hostname + ':' + str(port) + '/rest'

    try:
        if payload:
            resp = open_url(url=rest_url + '/' + url, method=method, headers=headers, url_username=username, url_password=password, force_basic_auth=True, validate_certs=validate_certs, data=json.dumps(payload))
        else:
            resp = open_url(url=rest_url + '/' + url, method=method, headers=headers, url_username=username, url_password=password, force_basic_auth=True, validate_certs=validate_certs)
        
        '''No Content'''
        if resp.code == 204:
            rest_result = {}
        elif resp.code > 199 and resp.code < 300:
            rest_result = json.loads(resp.read())
        else:
            _raise_or_fail(msg="Failed to process url " + url + " return code: " + str(resp.code))

    except Exception as e:
        _raise_or_fail(msg="REST API Call to " + url + " Failed! " + str(e))
        
    return rest_result

def gather_routeros_facts(hostname, port, username, password, validate_certs):
    
    rest_result = request_from_api(hostname=hostname, port=port, username=username, password=password, validate_certs=validate_certs, url='system/routerboard')
    facts = {}
    facts['firmware_version'] = str(rest_result['current-firmware'])
    facts['firmware_factory'] = str(rest_result['factory-firmware'])
    facts['firmware_type'] = str(rest_result['firmware-type'])
    facts['firmware_available'] = rest_result['upgrade-firmware']
    facts['model'] = str(rest_result['model'])
    facts['serial'] = rest_result['serial-number']
    if rest_result['routerboard'] == "true":
      facts['routerboard'] = True
    else:
      facts['routerboard'] = False

    rest_result = request_from_api(hostname=hostname, port=port, username=username, password=password, validate_certs=validate_certs, url='system/identity')
    facts['identity'] = str(rest_result['name'])

    rest_result = request_from_api(hostname=hostname, port=port, username=username, password=password, validate_certs=validate_certs, url='system/resource')

    facts['uptime'] = str(rest_result['uptime'])
    facts['build_time'] = str(rest_result['build-time'])
    facts['software_factory'] = str(rest_result['factory-software'])
    facts['memory_free'] = int(rest_result['free-memory'])
    facts['memory_total'] = int(rest_result['total-memory'])
    facts['cpu'] = str(rest_result['cpu'])
    facts['cpu_count'] = int(rest_result['cpu-count'])
    facts['cpu_frequency'] = int(rest_result['cpu-frequency'])
    facts['cpu_load'] = int(rest_result['cpu-load'])
    facts['hdd_free'] = int(rest_result['free-hdd-space'])
    facts['hdd_total'] = int(rest_result['total-hdd-space'])
    facts['architecture'] = str(rest_result['architecture-name'])
    facts['board_name'] = str(rest_result['board-name'])
    facts['platform'] = str(rest_result['platform'])
    
    return facts

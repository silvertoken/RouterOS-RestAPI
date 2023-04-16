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

DOCUMENTATION = '''
---
module: routeros.dns
author: "silvertoken (@silvertoken)"
short_description: Manage the static DNS entries using MikroTik RouterOS REST API
description:
  - This module can be used to create, delete, or update the static DNS entries.
options:
  name:
    description:
    - Fully qualified domain name of the DNS entry.
    required: true
    type: str
  ip:
    description:
    - IP Address for the DNS entry.
    required: false
    type: str
  enabled:
    description:
    - Enable or disable the DNS entry.
    required: false
    type: bool
  ttl:
    description:
    - Time to live of the DNS entry.
    required: false
    type: str
  state:
    description:
    - State of the DNS entry
    - If set to C(present) the DNS entry will be created or updated.
    - If set to C(absent) the DNS entry will be removed
    default: present
    type: str
    required: false
    choices: [ present, absent]
extends_documentation_fragment:
  - silvertoken.routeros.routeros.documentation
    
'''

EXAMPLES = """
- name: Add DNS Entry
  silvertoken.routeros.dns:
    hostname: router.localdomain
    username: admin
    password: ****
    name: test.localdomain
    ip: "10.10.10.10"
  delegate_to: localhost
    
- name: Remove DNS Entry
  silvertoken.routeros.dns:
    hostname: router.localdomain
    username: admin
    password: ****
    name: test.localdomain
    ip: "10.10.10.10"
    state: absent
  delegate_to: localhost
"""

RETURN = """
result:
  description: The details of the DNS entry
  returned: On success
  type: dict
  contains:
    name:
      description: Fully qualified domain name of the DNS entry
      type: str
    ip:
      description: IP address of the DNS entry
      type: str
    enabled:
      description: Enable state of the DNS entry
      type: str
    ttl:
      description: Time to live of the DNS entry
      type: str
    id:
      description: ID of the DNS entry
      type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.silvertoken.routeros.plugins.module_utils.routeros import routeros_argument_spec, request_from_api

def get_dns(module, name):
    rest_result = request_from_api(module=module, url='ip/dns/static')
    for dns in rest_result:
        if dns['name'] == name:
            return dns
    return None

def main():
    module_args = routeros_argument_spec()
    module_args.update(
      name=dict(type='str', required=True),
      ip=dict(type='str', required=False),
      state=dict(type='str',
                 choices=['present', 'absent'],
                 default='present'),
      enabled=dict(type='str',
                   required=False,
                   default="true"),
      ttl=dict(type='str', required=False),
      
    )

    ansible_result = dict(
        changed=False,
        result=dict()
    )
    
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.params.get('enabled') == "false":
        disabled = "true"
    else:
        disabled = "false"
    
    dns_obj = get_dns(module, module.params.get('name'))
        
    if module.params.get('state') == 'present':
        if dns_obj:
            if dns_obj['address'] != module.params.get('ip') or dns_obj['disabled'] != disabled or (module.params.get('ttl') and dns_obj['ttl'] != module.params.get('ttl')):
               ansible_result['changed'] = True
               ansible_result['result']['msg'] = "DNS entry with name '" + module.params.get('name') + "' will be updated"
               if not module.check_mode:
                    payload = {
                      "name": module.params.get('name'),
                      "address": module.params.get('ip'),
                      "disabled": disabled
                    }
                    if module.params.get('ttl'):
                          payload['ttl'] = module.params.get('ttl')
                    rest_result = request_from_api(module, method='PUT', url='ip/dns/static/' + dns_obj['.id'], payload=payload)
                    ansible_result['result']['id'] = rest_result['.id']
                    ansible_result['result']['name'] = rest_result['name']
                    ansible_result['result']['ip'] = rest_result['address']
                    ansible_result['result']['ttl'] = rest_result['ttl']
                    if rest_result['disabled'] == "true":
                        ansible_result['result']['enabled'] = "false"
                    else:
                        ansible_result['result']['enabled'] = "true"
            else:
                ansible_result['result']['msg'] = "DNS entry with name '" + module.params.get('name') + "' already up to date"
        else:
            ansible_result['changed'] = True
            ansible_result['result']['msg'] = "DNS entry with name '" + module.params.get('name') + "' will be created"
            if not module.check_mode:
                payload = {
                    "name": module.params.get('name'),
                    "address": module.params.get('ip'),
                    "disabled": disabled
                }
                
                if module.params.get('ttl'):
                      payload['ttl'] = module.params.get('ttl')
                      
                rest_result = request_from_api(module, method='PUT', url='ip/dns/static', payload=payload)
                ansible_result['result']['id'] = rest_result['.id']
                ansible_result['result']['name'] = rest_result['name']
                ansible_result['result']['ip'] = rest_result['address']
                ansible_result['result']['ttl'] = rest_result['ttl']
                if rest_result['disabled'] == "true":
                    ansible_result['result']['enabled'] = "false"
                else:
                    ansible_result['result']['enabled'] = "true"
    elif module.params.get('state') == 'absent':            
        if dns_obj:
            ansible_result['changed'] = True
            ansible_result['result']['msg'] = "DNS entry with name '" + module.params.get('name') + "' will be removed"
            if not module.check_mode:
                rest_result = request_from_api(module, method='DELETE', url='ip/dns/static/' + dns_obj['.id'])
        else:
            ansible_result['changed'] = False
            ansible_result['result']['msg'] = "DNS entry with name '" + module.params.get('name') + "' does not exist"
    
    module.exit_json(**ansible_result)
    
if __name__ == "__main__":
    main()
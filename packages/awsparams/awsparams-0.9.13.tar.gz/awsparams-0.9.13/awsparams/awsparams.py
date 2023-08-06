#!/usr/bin/env python3.6
# Copyright 2016 Brigham Young University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import boto3
from getpass import getpass
__VERSION__ = '0.9.13'


def connect_ssm(profile=''):
    if profile:
        session = boto3.Session(profile_name=profile)
        ssm = session.client('ssm')
    else:
        ssm = boto3.client('ssm')
    return ssm


def put_parameter(profile, overwrite, parameter):
    ssm = connect_ssm(profile)
    if overwrite:
        parameter['Overwrite'] = True
    ssm.put_parameter(**parameter)


def remove_parameter(profile, param):
    ssm = connect_ssm(profile)
    ssm.delete_parameter(Name=param)


def get_parameter_value(name, decryption=False, profile=None):
    ssm = connect_ssm(profile)
    param = ssm.get_parameters(Names=[name], WithDecryption=decryption)['Parameters'][0]
    return param['Value']


def get_parameter(name, profile=None, values=False, decryption=False):
    ssm = connect_ssm(profile)
    _params = ssm.describe_parameters(Filters=[{'Key': 'Name', 'Values': [name]}])['Parameters']
    assert len(_params) == 1
    result = build_param_result(_params[0], profile, values, decryption)
    if result['Name'] != name:
        return
    return result


def build_param_result(param, profile, values=False, decryption=False):
    result = {
        'Name': param['Name'],
        'Value': get_parameter_value(param['Name'], decryption, profile) if values else None,
        'Type': param['Type']
    }

    if param.get('Description'):
        result['Description'] = param['Description']
    if param.get('KeyId'):
        result['KeyId'] = param['KeyId']

    return result


def get_all_parameters(profile=None, pattern=None, values=False, decryption=False):
    ssm = connect_ssm(profile)
    parameter_page = ssm.describe_parameters()
    parameters = parameter_page['Parameters']
    while parameter_page.get('NextToken'):
        parameter_page = ssm.describe_parameters(
            NextToken=parameter_page['NextToken'])
        parameters.extend(parameter_page['Parameters'])

    if pattern:
        return [build_param_result(param, profile, values, decryption) for param in parameters if pattern in param['Name']]
    else:
        return [build_param_result(param, profile, values, decryption) for param in parameters]


def ls_param(src='', profile=None, values=False, with_decryption=False):
    """
    List Paramters, optional matching a specific prefix/pattern
    """
    if with_decryption and not values:
        values = True
    for parm in get_all_parameters(profile, src, values, with_decryption):
        if values:
            try:
                print("{}: {}".format(parm['Name'], parm['Value']))
            except Exception as err:
                print("Unknown error occured: {}".format(err))
        else:
            print(parm['Name'])


def cp_param(src, dst, src_profile='', dst_profile='', prefix=False, overwrite=False):
    """
    Copy a parameter, optionally across accounts
    """
    # cross account copy without needing dst
    if src_profile and dst_profile and src_profile != dst_profile and not dst:
        dst = src
    elif not dst:
        print("dst (Destination) is required when not copying to another profile")
        return
    if prefix:
        params = get_all_parameters(src_profile, src, values=True, decryption=True)
        for i in params:
            orignal_name = i['Name']
            i['Name'] = i['Name'].replace(src, dst)
            put_parameter(dst_profile, overwrite, i)
            print("Copied {} to {}".format(orignal_name, i['Name']))
        return True
    else:
        if isinstance(src, str):
            src_param = get_parameter(src, profile=src_profile, values=True, decryption=True)
            if not src_param:
                print("Parameter: {} not found".format(src))
                return

            src_param['Name'] = dst
            put_parameter(dst_profile, overwrite, src_param)
            print("Copied {} to {}".format(src, dst))
            return True


def mv_param(src, dst, prefix=False, profile=None):
    """
    Move or rename a parameter
    """
    if prefix:
        if cp_param(src, dst, src_profile=profile, dst_profile=profile, prefix=prefix):
            rm_param(src, force=True, prefix=True, profile=profile)
    else:
        if cp_param(src, dst, src_profile=profile, dst_profile=profile):
            rm_param(src, force=True, profile=profile)


def sanity_check(param, force):
    if force:
        return True
    sanity_check = input("Remove {} y/n ".format(param))
    return sanity_check == 'y'


def rm_param(src, force=False, prefix=False, profile=None):
    """
    Remove/Delete a parameter
    """
    if prefix:
        params = get_all_parameters(profile, src)
        if len(params) == 0:
            print("No parameters with the {} prefix found".format(src))
        else:
            for param in params:
                if sanity_check(param, force):
                    remove_parameter(profile, param['Name'])
                    print("The {} parameter has been removed".format(param['Name']))
    else:
        param = get_parameter(name=src, profile=profile)
        if 'Name' in param:
            if sanity_check(src, force):
                remove_parameter(profile, src)
                print("The {} parameter has been removed".format(src))
        else:
            print("Parameter {} not found".format(src))


def new_param(name, value, param_type='String', key='', description='', profile=None, overwrite=False):
    """
    Create a new parameter
    """
    if not value:
        if param_type == 'SecureString':
            value = getpass(prompt="SecureString: ")
        elif param_type == 'StringList':
            value = input("Input Values seperated by ',': ")
        elif param_type == 'String':
            value = input('Parameter Value: ')

    param = {
        'Name': name,
        'Value': value,
        'Type': param_type,
        'Overwrite': overwrite
    }
    if key:
        param['KeyId'] = key
    if description:
        param['Description'] = description
    put_parameter(profile, overwrite, param)


def set_param(src, value, profile=None):
    """
    Edit an existing parameter
    """
    existing_value = get_parameter_value(src, decryption=True, profile=profile)
    if existing_value != value:
        put = get_parameter(name=src, profile=profile, values=True, decryption=True)
        put['Value'] = value
        put_parameter(profile, True, put)
        print("updated param '{}' with value".format(src))
    else:
        print("not updated, param '{}' already contains that value".format(src))

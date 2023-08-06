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
import click
from .awsparams import ls_param, cp_param, mv_param, rm_param, new_param, set_param, __VERSION__


@click.group()
@click.version_option(version=__VERSION__)
def main():
    pass


@main.command('ls')
@click.argument('src', default='')
@click.option('--profile', type=click.STRING, help='profile to run with')
@click.option('-v', '--values', is_flag=True, help='display values')
@click.option('--with-decryption', is_flag=True, help='display decrypted values')
def ls(src='', profile=None, values=False, with_decryption=False):
    """
    List Paramters, optional matching a specific prefix/pattern
    """
    ls_param(src, profile, values, with_decryption)


@main.command('cp')
@click.argument('src')
@click.argument('dst', default='')
@click.option('--src_profile', type=click.STRING, default='', help="source profile")
@click.option('--dst_profile', type=click.STRING, default='', help="destination profile")
@click.option('--prefix', is_flag=True, help='copy set of parameters based on a prefix')
@click.option('--overwrite', is_flag=True, help='overwrite existing parameters')
def cp(src, dst, src_profile, dst_profile, prefix=False, overwrite=False):
    """
    Copy a parameter, optionally across accounts
    """
    cp_param(src, dst, src_profile, dst_profile, prefix, overwrite)

@main.command('mv')
@click.argument('src')
@click.argument('dst')
@click.option('--prefix', is_flag=True, help="move/rename based on prefix")
@click.option('--profile', type=click.STRING, help="alternative profile to use")
def mv(src, dst, prefix=False, profile=None):
    """
    Move or rename a parameter
    """
    mv_param(src, dst, prefix, profile)


@main.command('rm')
@click.argument('src')
@click.option('-f', '--force', is_flag=True, help='force without confirmation')
@click.option('--prefix', is_flag=True, help='remove/delete based on prefix')
@click.option('--profile', type=click.STRING, help='alternative profile to use')
def rm(src, force=False, prefix=False, profile=None):
    """
    Remove/Delete a parameter
    """
    rm_param(src, force, prefix, profile)


@main.command('new')
@click.option('--name', type=click.STRING, prompt="Parameter Name", help='parameter name')
@click.option('--value', type=click.STRING, help='parameter value')
@click.option('--param_type', type=click.STRING, default='String', help='parameter type one of String(default), StringList, SecureString')
@click.option('--key', type=click.STRING, default='', help='KMS Key used to encrypt the parameter')
@click.option('--description', type=click.STRING, default='', help='parameter description text')
@click.option('--profile', type=click.STRING, help='alternative profile to be used')
@click.option('--overwrite', is_flag=True, help='overwrite exisiting parameters')
def new(name=None, value=None, param_type='String', key='', description='', profile=None, overwrite=False):
    """
    Create a new parameter
    """
    new_param(name, value, param_type, key, description, profile, overwrite)


@main.command('set')
@click.argument('src')
@click.argument('value')
@click.option('--profile', type=click.STRING, default='', help="source profile")
def set(src=None, value=None, profile=None):
    """
    Edit an existing parameter
    """
    set_param(src, value, profile)


if __name__ == '__main__':
    main()

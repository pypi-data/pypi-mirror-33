# Why this script?

The current (Jul 2017) AWS Console for the Systems Manager Parameter
Store is good for adding and editing the values of parameters, but
misses key productivity functions like copying (especially en mass),
renaming, etc. The current `aws ssm` CLI is very similar in
functionality to the AWS Console.

This script is to automate a lot of the manual work currently needed
with the existing AWS-provided UIs.

# Installation

  - Install Python 3.6 with your favorite method. We recommend apt-get
    or rpm on linux, homebrew on mac and
    [here](https://www.python.org/downloads/) on windows.
  - `pip3.6 install awsparams`

# Usage

As a
Library:

``` sourceCode python
from awsparams.awsparams import get_parameter, get_all_parameters, get_parameter_value

#get a single parameter
param = get_parameter('test1', values=True, decryption=True)
# {'Name': 'test1', 'Value': 'test123', 'Type': 'SecureString', 'KeyId': 'alias/aws/ssm'}

# get multiple parameters with a prefix/pattern
params = get_all_parameters(profile=None, pattern="testing.testing.", values=True, decryption=True)
# [{'Name': 'testing.testing.testing', 'Value': '1234', 'Type': 'String'}, {'Name': 'testing.testing.testing2', 'Value': '1234', 'Type': 'String'}]

# get just a parameter value
value = get_parameter_value('test1', decryption=True, profile=None)
# test123
```

Usage can be referenced by running `awsparams --help` or `awsparams
subcommand --help` commands:

    Usage: awsparams [OPTIONS] COMMAND [ARGS]...
    
    Options:
    --version  Show the version and exit.
    --help     Show this message and exit.
    
    Commands:
    cp   Copy a parameter, optionally across accounts
    ls   List Paramters, optional matching a specific...
    mv   Move or rename a parameter
    new  Create a new parameter
    rm   Remove/Delete a parameter
    set  Edit an existing parameter

# Examples

## ls usage

ls names only: `awsparams ls`

ls with values no decryption: `awsparams ls --values` or `awsparams ls -v`

ls with values and decryption: `awsparams ls --with-decryption`

ls by prefix: `awsparams ls appname.prd`

## new usage

new interactively: `awsparams new`

new semi-interactively: `awsparams new --name appname.prd.username`

new non-interactive: `awsparams new --name appname.prd.usrname --value parameter_value
--description parameter_descripton`

## cp usage

copy a parameter: `awsparams cp appname.prd.username newappname.prd.username`

copy set of parameters with prefix appname.dev. to appname.prd.: `awsparams cp appname.dev. appname.prd. --prefix`

copy set of parameters starting with prefix repometa-generator.prd
overwrite existing parameters accross different accounts: `awsparams cp repometa-generator.prd --src_profile=dev --dst_profile=trn
--prefix=True`

copy single parameters accross different accounts: `awsparams cp appname.dev.username appname.trb.us`
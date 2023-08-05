import pytest
import boto3
from awsparams import awsparams
from moto import mock_ssm


@pytest.fixture
@mock_ssm
def fake_param():
    ssm = boto3.client('ssm')
    param = {
        'Name': 'fakeparam',
        'Type': 'String',
        'Value': 'fakevalue'
    }
    ssm.put_parameter(**param)
    yield param
    ssm.delete_parameter(Name=param['Name'])


@mock_ssm
def test_connect_ssm():
    assert awsparams.connect_ssm()


@mock_ssm
def test_put_parameter():
    ssm = boto3.client('ssm')
    param = {
        'Name': 'fakeparam',
        'Type': 'String',
        'Value': 'fakevalue'
    }
    awsparams.put_parameter(None, False, param)
    result = ssm.get_parameters(Names=['fakeparam'])['Parameters']
    assert result[0]['Name'] == param['Name']
    assert result[0]['Value'] == param['Value']
    assert result[0]['Type'] == param['Type']


@mock_ssm
def test_remove_parameter(fake_param):
    ssm = boto3.client('ssm')
    param = next(fake_param)
    awsparams.remove_parameter(None, param['Name'])
    result = ssm.get_parameters(Names=['fakeparam'])['Parameters']
    assert len(result) == 0


@mock_ssm
def test_get_parameter_value(fake_param):
    param = next(fake_param)
    result = awsparams.get_parameter_value(param['Name'])
    assert result == param['Value']


@mock_ssm
def test_get_parameter(fake_param):
    param = next(fake_param)
    result = awsparams.get_parameter(param['Name'], values=True)
    assert result == param


@mock_ssm
def test_build_param_result(fake_param):
    param = next(fake_param)
    result = awsparams.build_param_result(param, None, values=True)
    assert result == param


@mock_ssm
def test_get_all_parameters(fake_param):
    param = next(fake_param)
    ssm = boto3.client('ssm')
    param2 = {
        'Name': 'fakeparam2',
        'Type': 'String',
        'Value': 'fakevalue2'
    }
    ssm.put_parameter(**param2)
    result = awsparams.get_all_parameters(None, values=True)
    assert len(result) == 2

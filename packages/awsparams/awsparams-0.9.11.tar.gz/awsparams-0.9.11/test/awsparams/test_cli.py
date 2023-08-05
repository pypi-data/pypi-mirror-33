import pytest
from awsparams import cli
from click.testing import CliRunner
from moto import mock_ssm


@pytest.fixture
def cli_runner():
    return CliRunner()


@mock_ssm
def test_new(cli_runner):
    result = cli_runner.invoke(cli.new, ['--name', 'testing.testing.testing', '--value', '1234', '--param_type', 'SecureString'])
    cli_runner.invoke(cli.rm, ['testing.testing.testing', '-f'])
    assert result.exit_code == 0
    assert result.output.strip() == ''


@mock_ssm
def test_new_simple(cli_runner):
    result = cli_runner.invoke(cli.new, ['--name', 'testing.testing.testing', '--value', '1234'])
    assert result.exit_code == 0
    cli_runner.invoke(cli.rm, ['testing.testing.testing', '-f'])


@mock_ssm
def test_ls(cli_runner):
    cli_runner.invoke(cli.new, ['--name', 'testing.testing.testing', '--value', '1234', '--param_type', 'SecureString'])
    result = cli_runner.invoke(cli.ls, ['testing.testing.'])
    cli_runner.invoke(cli.rm, ['testing.testing.testing', '-f'])
    assert result.exit_code == 0
    assert result.output.strip() == "testing.testing.testing"


@mock_ssm
def test_ls_values(cli_runner):
    cli_runner.invoke(cli.new, ['--name', 'testing.testing.testing', '--value', '1234', '--param_type', 'SecureString'])
    result = cli_runner.invoke(cli.ls, ['testing.testing.', '-v', '--with-decryption'])
    cli_runner.invoke(cli.rm, ['testing.testing.testing', '-f'])
    assert result.exit_code == 0
    assert result.output.strip() == "testing.testing.testing: 1234"


@mock_ssm
def test_cp_basic(cli_runner):
    cli_runner.invoke(cli.new, ['--name', 'testing.testing.testing', '--value', '1234', '--param_type', 'SecureString'])
    result = cli_runner.invoke(cli.cp, ['testing.testing.testing', 'testing.testing.newthing'])
    cli_runner.invoke(cli.rm, ['testing.testing.testing', '-f'])
    assert result.exit_code == 0
    assert result.output.strip() == 'Copied testing.testing.testing to testing.testing.newthing'
    cli_runner.invoke(cli.rm, ['testing.testing.newthing', '-f'])


@mock_ssm
def test_cp_fail(cli_runner):
    result = cli_runner.invoke(cli.cp, ['testing.testing.testing'])
    assert result.exit_code == 0
    assert result.output.strip() == 'dst (Destination) is required when not copying to another profile'


@mock_ssm
def test_rm(cli_runner):
    cli_runner.invoke(cli.new, ['--name', 'testing.testing.testing', '--value', '1234'])
    result = cli_runner.invoke(cli.rm, ['testing.testing.testing', '-f'])
    assert result.exit_code == 0


@mock_ssm
def test_set(cli_runner):
    cli_runner.invoke(cli.new, ['--name', 'testing.testing.testing', '--value', '1234'])
    result = cli_runner.invoke(cli.set, ['testing.testing.testing', '4321'])
    second_result = cli_runner.invoke(cli.ls, ['testing.testing.testing', '--values'])
    assert result.exit_code == 0
    assert result.output.strip() == "updated param 'testing.testing.testing' with value"
    assert second_result.output.strip() == "testing.testing.testing: 4321"


@mock_ssm
def test_mv_simple(cli_runner):
    cli_runner.invoke(cli.new, ['--name', 'testing.testing.testing', '--value', '1234'])
    result = cli_runner.invoke(cli.mv, ['testing.testing.testing', 'testing1.testing1.testing1'])
    second_result = cli_runner.invoke(cli.ls, ['testing.testing.testing', '--values'])
    third_result = cli_runner.invoke(cli.ls, ['testing1.testing1.testing1', '--values'])
    assert result.exit_code == 0
    assert second_result.output.strip() == ""
    assert third_result.output.strip() == "testing1.testing1.testing1: 1234"

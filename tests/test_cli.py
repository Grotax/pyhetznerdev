"""
Test CLI interface
"""
from click.testing import CliRunner
from pyhetznerdev.cli import main


def test_cli_help():
    """Test that CLI help works"""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'pyhetznerdev' in result.output
    assert 'create' in result.output
    assert 'delete' in result.output


def test_cli_version():
    """Test that version command works"""
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert '0.1.0' in result.output


def test_create_help():
    """Test create command help"""
    runner = CliRunner()
    result = runner.invoke(main, ['create', '--help'])
    assert result.exit_code == 0
    assert 'Create a new development server' in result.output
    assert '--snapshot' in result.output
    assert '--floating-ip' in result.output


def test_delete_help():
    """Test delete command help"""
    runner = CliRunner()
    result = runner.invoke(main, ['delete', '--help'])
    assert result.exit_code == 0
    assert 'Delete a development server' in result.output
    assert '--keep-ip' in result.output


def test_config_help():
    """Test config command help"""
    runner = CliRunner()
    result = runner.invoke(main, ['config', '--help'])
    assert result.exit_code == 0
    assert 'Manage configuration settings' in result.output


def test_list_help():
    """Test list command help"""
    runner = CliRunner()
    result = runner.invoke(main, ['list', '--help'])
    assert result.exit_code == 0
    assert 'List all servers' in result.output

import pcc
from click.testing import CliRunner
from unittest.mock import patch


dummy_scripts = {
    'A': 'echo stuff',
    'D:test': 'other stuff',
}


@patch('pcc.load_scripts')
def test_print_script_keys(mock_load_scripts):
    mock_load_scripts.return_value = dummy_scripts
    runner = CliRunner()
    result = runner.invoke(pcc.main, ['--commands'])
    assert result.exit_code == 0
    assert result.output == 'A\nD:test\n'


def test_print_commands_does_nothing_if_off():
    assert pcc.print_commands(None, None, False) is None


@patch('pcc.load_scripts')
@patch('pcc.Popen')
def test_running_script(mock_popen, mock_load_scripts):
    mock_load_scripts.return_value = dummy_scripts
    runner = CliRunner()
    result = runner.invoke(pcc.main, ['A'])
    mock_popen.called_once_with(['echo', 'stuff'])
    assert result.exit_code == 0


@patch('pcc.load_scripts')
@patch('pcc.Popen')
def test_running_multiple_scripts(mock_popen, mock_load_scripts):
    mock_load_scripts.return_value = dummy_scripts
    runner = CliRunner()
    result = runner.invoke(pcc.main, ['A', 'D:test'])
    mock_popen.assert_any_call(['echo', 'stuff'], stdout=-1)
    mock_popen.assert_any_call(['other', 'stuff'], stdout=-1)
    assert result.exit_code == 0

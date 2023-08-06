import pccgui
from unittest.mock import patch, call
from click.testing import CliRunner


@patch('pccgui.print')
def test_print_header_contains_lines(mock_print):
    pccgui.print_header('a simple line')
    calls = [
        call('╔═══════════════╗'),
        call('║ a simple line ║'),
        call('╚═══════════════╝'),
    ]
    assert mock_print.call_args_list == calls


@patch('pccgui.Popen')
def test_script_wrapper_would_start_process_with_a_list(mock_popen):
    wrapper = pccgui.script_wrapper('command list')
    wrapper()
    mock_popen.called_with_args(['command', 'list'])


@patch('pccgui.load_scripts')
@patch('pccgui.Tk')
def test_tk_window(mock_tk, mock_load_scripts):
    raw_data = {
        'run:a': 'echo A',
        # 'run:b': 'echo B',
    }
    mock_load_scripts.return_value = raw_data
    runner = CliRunner()
    results = runner.invoke(pccgui.main)
    assert results.exit_code == 0
    mock_tk.title.called_once_with('Python Command Center')

from utils import load_scripts
from contextlib import contextmanager
import os


@contextmanager
def temp_file(file_path, file_text):
    with open(file_path, 'w') as f:
        f.write(file_text)
    yield f
    os.remove(file_path)


def test_loads_pcc_file():
    raw_json = '{"a": "echo stuff", "b": "echo other"}'
    raw_dict = {
        'a': 'echo stuff',
        'b': 'echo other',
     }
    with temp_file('pcc.json', raw_json):
        loaded_data = load_scripts()
        assert raw_dict == loaded_data


def test_returns_none_if_missing():
    assert load_scripts() is None

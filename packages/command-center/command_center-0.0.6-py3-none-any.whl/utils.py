import os
import json


def load_scripts():
    if os.path.isfile('pcc.json'):
        with open('pcc.json') as f:
            return json.load(f)

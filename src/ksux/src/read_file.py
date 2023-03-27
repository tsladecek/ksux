import json
import logging
from json import JSONDecodeError
from typing import Dict, List, Union

import yaml
from yaml import YAMLError


def read_json(path: str) -> List[Dict]:
    with open(path) as f:
        try:
            decoded = json.load(f)
        except JSONDecodeError:
            logging.error(f'Failed to parse {path}. JSON invalid')
            exit(1)
        else:
            if type(decoded) == dict:
                decoded = [decoded]

            return decoded


def load_yaml(yaml_str: str, path: str) -> Union[Dict, List[Dict]]:
    try:
        yaml_file = yaml.safe_load(yaml_str)
    except YAMLError as exc:
        logging.error(f'Failed to parse {path}. YAML invalid')
        exit(1)
    else:
        return yaml_file


def read_yaml(path: str) -> List[Dict]:
    decoded = []

    # 1. read the file
    with open(path) as f:
        # strip manifest divisor if it is in the beginning or in the end
        raw = f.read()

    # 2. Check if items are separated by "---"
    if "---" in raw:
        raw = raw.strip('---').split('---')
        for r in raw:
            y = load_yaml(r, path)
            decoded.append(y)

        return decoded

    # 3. The file should be readable as is by yaml safe load
    decoded = load_yaml(raw, path)
    # return list of dicts
    if type(decoded) == dict:
        decoded = [decoded]

    return decoded

import json
import logging
from json import JSONDecodeError
from pathlib import Path

from yaml import safe_load, YAMLError


def read_json(path: str):
    with open(path) as f:
        try:
            decoded = json.load(f)
        except JSONDecodeError:
            logging.error(f'Failed to parse {path}. JSON invalid')
            exit(1)
        else:
            return decoded


def read_yaml(path: str):
    try:
        decoded = safe_load(Path(path).read_text())
    except YAMLError as exc:
        logging.error(f'Failed to parse {path}. YAML invalid')
        exit(1)
    else:
        return decoded

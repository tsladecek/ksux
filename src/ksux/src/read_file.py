import json
import logging
from json import JSONDecodeError
from typing import Dict, List, Union

from ruamel.yaml import CommentedMap, CommentedSeq, YAML
from ruamel.yaml.composer import ComposerError


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


def load_yaml(yaml_str: str, path: str) -> Union[CommentedMap, CommentedSeq]:
    yaml = YAML()
    yaml.preserve_quotes = True
    try:
        yaml_file = yaml.load(yaml_str)
    except ComposerError:
        logging.error(f'Failed to parse {path}. YAML invalid')
        exit(1)
    else:
        return yaml_file


def read_yaml(path: str) -> Union[List[Dict], List[CommentedMap]]:
    decoded = []

    # 1. read the file
    with open(path) as f:
        # strip manifest divisor if it is in the beginning or in the end
        raw = f.readlines()

        # ignore comments
        raw = ''.join([i for i in raw if not i.startswith('#')])

    # 2. Check if items are separated by "---"
    if "---" in raw:
        raw = raw.strip('---').split('---')
        for r in raw:
            y = load_yaml(r, path)
            decoded.append(y)

        return decoded

    # 3. The file should be readable as is by yaml safe load
    yaml_decoded = load_yaml(raw, path)
    # return list of dicts
    if type(yaml_decoded) == CommentedMap:
        decoded = [yaml_decoded]
    elif type(yaml_decoded) == CommentedSeq:
        for cm in yaml_decoded:
            decoded.append(cm)

    return decoded

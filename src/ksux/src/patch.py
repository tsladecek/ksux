import logging
import os
from copy import copy
from typing import List, Dict, Union

from pydantic import ValidationError
from ruamel.yaml import CommentedMap, CommentedSeq

from .read_file import read_yaml, read_json
from .schemas import Op, Patch, Action


def validate_patch(patch: dict) -> Patch:
    """
    Validate patch
    :param patch: patch object
    :return:
    """
    try:
        validated = Patch(**patch)
    except ValidationError:
        logging.error(f'Patch {patch} did not pass validation. See required fields')
        exit(1)
    else:
        return validated


def read_patches(patches_dir: str, exclude: List[str] = []) -> List[Patch]:
    """
    Read and validate patches
    :param patches_dir: directory with patches
    :param exclude: exclude pattern ["{apiVersion}_{kind}_{name}", ...]
    :return: list of patches
    """
    patches = []
    for p in os.listdir(patches_dir):
        file_path = os.path.join(patches_dir, p)

        if p.endswith('yaml') or p.endswith('yml'):
            temp = read_yaml(file_path)
        elif p.endswith('json'):
            temp = read_json(file_path)
        else:
            continue

        for pi in temp:
            validated = validate_patch(pi)
            if f'{validated.target.apiVersion}_{validated.target.kind}_{validated.target.name}' not in exclude:
                patches.append(validated)

    return patches


def get_real_path(patch: Patch, op: Op, manifest: dict):
    """
    Construct path to index into the manifest. This will handle cases when it is desired
    to select a member of a list with a name
    :param patch: Patch object
    :param op: Operation object
    :param manifest: manifest which will be patched
    :return: path (as a python) list composed of keys and indexes
    """

    path = op.path.strip('/').split('/')
    path = path[1:] if path[0] == '' else path

    current_manifest = copy(manifest)
    path_real = []
    for pi, path_param in enumerate(path):
        if type(current_manifest) in [dict, CommentedMap]:
            # If path_param is last this could be a valid option if op is ADD
            if pi == len(path) - 1 and path_param not in current_manifest:
                current_manifest[path_param] = ''
            else:
                try:
                    current_manifest = current_manifest[path_param]
                except KeyError:
                    logging.error(f'{path} is not correct for patch={patch.__dict__}, op={op.__dict__}')
                    exit(1)

            path_real.append(path_param)
        elif type(current_manifest) in [list, CommentedSeq]:
            # look for item with name == path_param
            idx = -1
            for i, item in enumerate(current_manifest):
                if item[op.list_key] == path_param:
                    idx = i

            if idx == -1:
                logging.error(f'Patch {patch.__dict__} at path {path} does not contain an item with name={path_param}')
                exit(1)
            else:
                path_real.append(idx)
                current_manifest = current_manifest[idx]
        else:
            logging.error('Manifest must be composed of dicts and lists')
            exit(1)
    return path_real


def apply_patch(patch: Patch, op: Op, manifest: Union[Dict, CommentedMap]) -> Union[Dict, CommentedMap]:
    """
    Applies patch and updates a manifest
    :param patch: Patch Object
    :param op: Operation Object
    :param manifest: original manifest
    :return: patched manifest
    """
    path_real = get_real_path(patch=patch, op=op, manifest=manifest)

    temp = manifest
    for i in path_real[:-1]:
        temp = temp[i]

    if op.action == Action.replace:
        if type(temp) in [dict, CommentedMap]:
            temp[path_real[-1]] = op.value
        else:
            raise ValueError('Integer cant be last index for replace')
    elif op.action == Action.add:
        if type(temp[path_real[-1]]) in [dict, CommentedMap]:
            temp[path_real[-1]].update(op.value)
        elif type(temp[path_real[-1]]) in [dict, CommentedSeq]:
            temp[path_real[-1]].append(op.value)
        else:
            logging.error('Last index must map to a list or a dict')
    elif op.action == Action.remove:
        del temp[path_real[-1]]

    return manifest


def patch_manifest(patch: Patch, manifests: Dict) -> Dict:
    """
    Apply all ops in a patch to a manifest
    :param patch: Patch Object
    :param manifests: all manifests
    :return: patched manifest
    """
    try:
        m = manifests[patch.target.apiVersion][patch.target.kind][patch.target.name]
    except KeyError:
        logging.error(f'Patch {patch.__dict__} targets unknown manifest. Make sure '
                      f'that manifest with specified apiVersion, kind and name exists')
    else:
        for op in patch.ops:
            m = apply_patch(patch, op, m)
        return m

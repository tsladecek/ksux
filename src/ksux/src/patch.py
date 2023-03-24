import logging
import os
from copy import copy
from typing import List, Dict

from pydantic import ValidationError

from .read_file import read_yaml, read_json
from .schemas import Op, Patch, Action


def validate_patch(validated_patches: List[Patch], patch: dict) -> None:
    """
    Validate patch
    :param validated_patches: list of validated_patches
    :param patch:
    :return:
    """
    try:
        validated = Patch(**patch)
    except ValidationError:
        logging.error(f'Patch {patch} did not pass validation. See required fields')
        exit(1)
    else:
        validated_patches.append(validated)


def read_patches(patches_dir: str) -> List[Patch]:
    """
    Read and validate patches
    :param patches_dir: directory with patches
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

        if type(temp) != list:
            logging.error('Patches File should be a list of patches')
            exit(1)

        for pi in temp:
            validate_patch(patches, pi)

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
        if type(current_manifest) == dict:

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
        elif type(current_manifest) == list:
            # look for item with name == path_param
            idx = -1
            for i, item in enumerate(current_manifest):
                if item['name'] == path_param:
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


def apply_patch(patch: Patch, op: Op, manifest: dict):
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
        if type(temp) == dict:
            temp[path_real[-1]] = op.value
        else:
            raise ValueError('Integer cant be last index for replace')
    elif op.action == Action.add:
        if type(temp[path_real[-1]]) == dict:
            temp[path_real[-1]].update(op.value)
        elif type(temp[path_real[-1]]) == list:
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

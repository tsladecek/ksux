import json
from functools import reduce
from operator import getitem
from typing import List, Union

from .schemas import Op, Patch, Action


def patch_add(op: Op, manifest):
    pass


def patch_replace(op: Op, manifest):
    pass


def patch_remove(op: Op, manifest):
    pass


def get_real_path(patch: Patch, op: Op, path: list, manifest: dict):
    current_manifest = manifest
    path_real = []
    for path_param in path:
        if type(current_manifest) == dict:
            try:
                current_manifest = current_manifest[path_param]
            except KeyError:
                print(f'{path} is not correct for patch={patch.__dict__}, op={op.__dict__}')
                exit(1)
            else:
                path_real.append(path_param)
        elif type(current_manifest) == list:
            # look for item with name == path_param
            idx = -1
            for i, item in enumerate(current_manifest):
                if item['name'] == path_param:
                    idx = i

            if idx == -1:
                print(f'Patch {patch.__dict__} at path {path} does not contain an item with name={path_param}')
                exit(1)
            else:
                path_real.append(idx)
        else:
            print('Manifest must be composed of dicts and lists')
            exit(1)
    return path_real


def apply_patch(patch: Patch, op: Op, manifest):
    path = op.path.strip('/').split('/')
    path = path[1:] if path[0] == '' else path

    path_real = get_real_path(patch=patch, op=op, path=path, manifest=manifest)

    temp = manifest
    for i in path_real[-1]:
        temp = temp[i]

    if op.action == Action.replace:
        if type(temp) == dict:
            temp[path_real[-1]] = op.value
    elif op.action == Action.add:
        val = json.loads(op.value)
        temp[path_real[-1]] = val
    elif op.action == Action.remove:
        temp[path_real[-1]] = {}


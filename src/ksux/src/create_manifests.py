import os
from typing import Dict, List

from pydantic import ValidationError

from .patch import apply_patch
from .read_file import read_yaml, read_json
from .schemas import Patch


def add_manifest(manifests_all: dict, manifest: dict) -> None:
    try:
        apiVersion = manifest['apiVersion']
        kind = manifest['kind']
        name = manifest['metadata']['name']
    except KeyError:
        print('apiVersion, kind and/or metadata.name key is not present')
        exit(1)
    else:
        if apiVersion not in manifests_all:
            manifests_all[apiVersion] = {}

        if kind not in manifests_all[apiVersion]:
            manifests_all[apiVersion][kind] = {}

        if name in manifests_all[apiVersion][kind]:
            print('There are two manifests with the same apiVersion, kind and name. This is forbidden')
            exit(1)
        else:
            manifests_all[apiVersion][kind][name] = manifest


def read_manifests(base_dir: str) -> Dict:
    manifests = {}
    for m in os.listdir(base_dir):
        file_path = os.path.join(base_dir, m)
        if m.endswith('yaml') or m.endswith('yml'):
            temp = read_yaml(file_path)
            add_manifest(manifests, temp)
        elif m.endswith('.json'):
            temp = read_json(file_path)
            add_manifest(manifests, temp)

    return manifests


def add_patch(patches: List[Patch], patch: dict) -> None:
    try:
        validated = Patch(**patch)
    except ValidationError:
        print(f'Patch {patch} did not pass validation. See required fields')
        exit(1)
    else:
        patches.append(validated)


def read_patches(patches_dir: str) -> List[Patch]:
    patches = []
    for p in os.listdir(patches_dir):
        file_path = os.path.join(patches_dir, p)
        if p.endswith('yaml') or p.endswith('yml'):
            temp = read_yaml(file_path)

            if type(temp) != list:
                print('Patches File should be a list of patches')
                exit(1)

            for pi in temp:
                add_patch(patches, pi)

    return patches


def patch_manifest(patch: Patch, manifests: Dict) -> Dict:
    try:
        m = manifests[patch.target.apiVersion][patch.target.kind][patch.target.name]
    except KeyError:
        print(f'Patch {patch.__dict__} targets unknown manifest. Make sure '
              f'that manifest with specified apiVersion, kind and name exists')
    else:
        for op in patch.ops:
            m = apply_patch(patch, op, m)
        return m


def create_manifests(base_dir: str, patches_dir: str):
    manifests = read_manifests(base_dir=base_dir)
    patches = read_patches(patches_dir=patches_dir)

    patched = []
    for patch in patches:
        patched.append(patch_manifest(patch, manifests))

    return patched

import logging
import os
from typing import Dict, List, Tuple

from .patch import read_patches, patch_manifest
from .read_file import read_yaml, read_json

logging.basicConfig(level=logging.DEBUG)


def add_manifest(manifests_index: dict, manifest: dict) -> None:
    """
    Add manifest to manifests_index
    :param manifests_index: index of manifests
    :param manifest: manifest to be added
    """
    try:
        apiVersion = manifest['apiVersion']
        kind = manifest['kind']
        name = manifest['metadata']['name']
    except KeyError:
        logging.error('apiVersion, kind and/or metadata.name key is not present')
        exit(1)
    else:
        if apiVersion not in manifests_index:
            manifests_index[apiVersion] = {}

        if kind not in manifests_index[apiVersion]:
            manifests_index[apiVersion][kind] = {}

        if name in manifests_index[apiVersion][kind]:
            logging.error('There are two manifests with the same apiVersion, kind and name. This is forbidden')
            exit(1)
        else:
            manifests_index[apiVersion][kind][name] = manifest


def read_manifests(base_dir: str, exclude: List[str] = []) -> Dict:
    """
    Read manifests from the base dir and create a manifest index
    :param base_dir: directory with manifest templates
    :param exclude: exclude pattern ["{apiVersion}_{kind}_{name}", ...]
    :return: manifest index
    """
    manifests = {}
    for m in os.listdir(base_dir):
        file_path = os.path.join(base_dir, m)
        if m.endswith('yaml') or m.endswith('yml'):
            temp = read_yaml(file_path)
        elif m.endswith('.json'):
            temp = read_json(file_path)
        else:
            logging.info(f'Unknown extension ".{m.split(".")[-1]}". Skipping...')
            continue

        for manifest in temp:
            if f'{manifest["apiVersion"]}_{manifest["kind"]}_{manifest["metadata"]["name"]}' not in exclude:
                add_manifest(manifests, manifest)

    return manifests


def patch_manifests(base_dir: str, patches_dir: str, exclude: List[str]) -> Tuple[List[Dict], Dict]:
    """
    Patch all manifests
    :param base_dir: directory with manifest templates
    :param patches_dir: patches directory
    :param exclude: exclude pattern ["{apiVersion}_{kind}_{name}", ...]
    :return: list of patched manifests + all manifests
    """
    manifests = read_manifests(base_dir=base_dir, exclude=exclude)
    patches = read_patches(patches_dir=patches_dir, exclude=exclude)

    patched = []
    for patch in patches:
        patched.append(patch_manifest(patch, manifests))

    return patched, manifests

import os
from copy import deepcopy

import pytest
from pydantic import ValidationError

from src.ksux.src.patch import read_patches, get_real_path, apply_patch
from src.ksux.src.schemas import Patch, Op, Action
from src.ksux.tests.config import settings


def get_valid_patch() -> dict:
    return {
        "name": "valid patch",
        "target": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "name": "deploy"
        },
        "ops": [
            {
                "name": "example op",
                "path": "/spec/replicas",
                "action": "replace",
                "value": 2
            }
        ]
    }


def test_validate_patch_valid_patch():
    valid = get_valid_patch()
    assert Patch(**valid)

    # value can be omitted for action remove
    valid_patch_action_remove_missing_value = get_valid_patch()
    valid_patch_action_remove_missing_value['ops'][0]['action'] = 'remove'
    del valid_patch_action_remove_missing_value['ops'][0]['value']

    assert Patch(**valid_patch_action_remove_missing_value)


def test_validate_patch_missing_field():
    # All fields must be present
    invalid_patch_missing_target_name = get_valid_patch()
    del invalid_patch_missing_target_name['target']['name']

    with pytest.raises(ValidationError) as exc:
        Patch(**invalid_patch_missing_target_name)

    # Value must be present for action replace or add
    invalid_patch_missing_value_for_replace_add = get_valid_patch()
    del invalid_patch_missing_value_for_replace_add['ops'][0]['value']

    for a in ['replace', 'add']:
        invalid_patch_missing_value_for_replace_add['ops'][0]['action'] = a

        with pytest.raises(ValueError) as exc:
            Patch(**invalid_patch_missing_value_for_replace_add)


def test_validate_patch_add_check_type():
    patch_add = get_valid_patch()
    patch_add['ops'][0]['action'] = 'add'
    patch_add['ops'][0]['value'] = {'key': 'val'}

    assert Patch(**patch_add)

    invalid_patch_value_for_add_not_object = get_valid_patch()
    invalid_patch_value_for_add_not_object['ops'][0]['action'] = 'add'
    invalid_patch_value_for_add_not_object['ops'][0]['value'] = 'val'

    with pytest.raises(ValueError):
        Patch(**invalid_patch_value_for_add_not_object)


def test_read_patches():
    p = read_patches(os.path.join(settings.PARENT, 'data', 'patches'))

    assert type(p) == list
    assert len(p) > 0


def test_get_real_path():
    manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "deploy"
        },
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": "container1",
                            "image": "nginx"
                        },
                        {
                            "name": "container2",
                            "image": "redis"
                        },
                        {
                            "name": "container3",
                            "image": "mariadb"
                        },
                        {
                            "name": "container4",
                            "image": "python"
                        },
                    ]
                }
            }
        }
    }

    patch = Patch(**get_valid_patch())

    for i in range(1, 5):
        patch.ops[0].path = f'/spec/template/spec/containers/container{i}/image'
        grp = get_real_path(patch, patch.ops[0], manifest)

        assert grp == ['spec', 'template', 'spec', 'containers', i - 1, 'image']


def test_patch_manifest():
    manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "deploy"
        },
        "spec": {
            "template": {
                "spec": {
                    "replicas": 1,
                    "containers": [
                        {
                            "name": "container1",
                            "image": "nginx"
                        }
                    ]
                }
            }
        }
    }

    replicas = '5'
    new_image_name = 'new-image-name'
    new_image = 'redis'

    patched_manifest_real = deepcopy(manifest)
    patched_manifest_real['spec']['template']['spec']['replicas'] = replicas
    patched_manifest_real['spec']['template']['spec']['containers'][0]['name'] = new_image_name
    patched_manifest_real['spec']['template']['spec']['containers'][0]['image'] = new_image

    patch = Patch(**get_valid_patch())
    patch.ops = [
        Op(name='replicas', path='/spec/template/spec/replicas', action=Action.replace, value=replicas),
        Op(name='image name', path='/spec/template/spec/containers/container1/name', action=Action.replace,
           value=new_image_name),
        Op(name='image', path=f'/spec/template/spec/containers/{new_image_name}/image', action=Action.replace,
           value=new_image)
    ]

    patched_manifest = apply_patch(patch, patch.ops[0], manifest)
    patched_manifest = apply_patch(patch, patch.ops[1], patched_manifest)
    patched_manifest = apply_patch(patch, patch.ops[2], patched_manifest)


def test_patch_ingress():
    """Patch Ingress resource

    Just an example, since ingress contains host field instead of name
    """

    NEW_HOST = 'new_host'

    manifest = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": "ingress"
        },
        "spec": {
            "rules": [
                {
                    "host": "host1",
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": "svc",
                                        "port": {
                                            "number": 80
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }

    patch_dict = {
        "name": "ingress patch",
        "target": {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "name": "ingress"
        },
        "ops": [
            {
                "name": "replace host",
                "path": "/spec/rules/host1/host",
                "action": "replace",
                "value": NEW_HOST,
                "list_key": "host"
            }
        ]
    }
    patch = Patch(**patch_dict)

    patched = apply_patch(patch, patch.ops[0], manifest)

    assert patched['spec']['rules'][0]['host'] == NEW_HOST

import os

from src.ksux.src.read_file import read_yaml, read_json
from src.ksux.tests.config import settings


def test_read_yaml_resources_separated_by_dashes():
    f = read_yaml(os.path.join(settings.PARENT, 'data', 'read_file', 'two_deployments_separated_by_dashes.yaml'))

    assert type(f) == list
    assert len(f) == 2


def test_read_yaml_resources_as_yaml_list():
    f = read_yaml(os.path.join(settings.PARENT, 'data', 'read_file', 'two_deployments_in_valid_yaml_format.yml'))

    assert type(f) == list
    assert len(f) == 2


def test_read_json():
    f = read_json(os.path.join(settings.PARENT, 'data', 'read_file', 'service_in_json_format.json'))

    assert type(f) == list
    assert len(f) == 1

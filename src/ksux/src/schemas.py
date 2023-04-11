import enum
from typing import Optional, Union, List

from pydantic import BaseModel, validator
from ruamel.yaml import CommentedSeq, CommentedMap


class Target(BaseModel):
    """
    Target object used to find a manifest. This should be a unique
    combination able to detect only one manifest
    """
    apiVersion: str
    kind: str
    name: str


class Action(enum.Enum):
    """Patching actions"""
    add = 'add'
    replace = 'replace'
    remove = 'remove'


class Op(BaseModel):
    """
    Operation

    name: name of the operation
    path: path to the resource in the manifest. In case of list
          you can use item names instead of indexes
    value: value to be added or which will replace old value. Not
           required for action = remove
    action: Action
    """
    name: str
    path: str
    value: Optional[Union[str, int, dict, list]]
    action: Action
    list_key: str = 'name'

    @validator('action')
    def check_value(cls, v, values, **kwargs):
        if v == Action.add or v == Action.replace:
            if 'value' not in values or values['value'] is None:
                raise ValueError(f'Value needs to be present for action {v}')

            # For add the value needs to be an object
            if v == Action.add and type(values['value']) not in [list, dict, CommentedMap, CommentedSeq]:
                raise ValueError('For add, the value needs to be a dict or a list')
        return v


class Patch(BaseModel):
    """Patch object"""
    name: str
    target: Target
    ops: List[Op]

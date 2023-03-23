import enum
from typing import Optional, Union, List

from pydantic import BaseModel, validator


class Target(BaseModel):
    apiVersion: str
    kind: str
    name: str


class Action(enum.Enum):
    add = 'add'
    replace = 'replace'
    remove = 'remove'


class Op(BaseModel):
    name: str
    path: str
    value: Optional[Union[str, int]]
    action: Action

    @validator('action')
    def check_value(cls, v, values, **kwargs):
        if v == Action.add.name or v == Action.replace.name:
            if 'value' not in values or values['value'] is None:
                raise ValueError(f'Value needs to be present for action {v}')
        return v

    class Config:
        use_enum_values = True


class Patch(BaseModel):
    name: str
    target: Target
    ops: List[Op]

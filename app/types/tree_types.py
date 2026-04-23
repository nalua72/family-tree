from typing import TypedDict


class NodeDict(TypedDict):
    id: str
    name: str
    first_surname: str
    second_surname: str


class EdgeDict(TypedDict):
    source: str
    target: str
    type: str

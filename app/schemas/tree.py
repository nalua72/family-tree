from pydantic import BaseModel


class PersonNode(BaseModel):
    id: str
    name: str
    first_surname: str
    second_surname: str


class PersonEdge(BaseModel):
    source: str
    target: str
    type: str


class PersonTreeResponse(BaseModel):
    root: str
    nodes: list[PersonNode]
    edges: list[PersonEdge]

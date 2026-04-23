import uuid
from sqlalchemy.orm import Session
from typing import Iterable

from app.db.base import Person
from app.repositories.person_repository import (get_children, get_parents)
from app.types.tree_types import (NodeDict, EdgeDict)


def map_person_to_node(person) -> NodeDict:
    return {
        "id": str(person.uuid),
        "name": person.first_name,
        "first_surname": person.first_surname,
        "second_surname": person.second_surname
    }


def get_neighbors(session: Session, person_uuid: uuid.UUID) -> list[tuple[str, Iterable[Person]]]:
    return [
        ("down", get_children(session, person_uuid)),
        ("up", get_parents(session, person_uuid)),
    ]


def build_edge(direction: str, current_id: str, neighbor_id: str) -> EdgeDict:
    if direction == "down":
        return (current_id, neighbor_id, "parent")
    else:
        return (neighbor_id, current_id, "child")

import uuid
from sqlalchemy.orm import Session
from collections import deque

from app.services.person_service import (get_person_by_id_service)
from app.repositories.person_repository import (get_children, get_parents)


def get_person_tree_service(session: Session, person_uuid: uuid.UUID, depth: int) -> dict:

    person = get_person_by_id_service(session, person_uuid)

    queue: list[tuple(uuid.UUID, int)] = deque([(person_uuid, 0)])
    visited: set[uuid.UUID] = {person_uuid}
    nodes_id: set[str] = {str(person_uuid)}
    edges_set: set[tuple[str, str]] = set()

    nodes = [{"id": str(person_uuid), "name": person.first_name,
              "first_surname": person.first_surname, "second_surname": person.second_surname}]
    edges = []

    data = {
        "root": str(person_uuid),
        "nodes": nodes,
        "edges": edges
    }

    while queue:

        current_uuid, level = queue.popleft()

        next_level = level + 1

        children = get_children(session, current_uuid)
        for child in children:

            if next_level <= depth:

                if str(child.uuid) not in nodes_id:
                    nodes_id.add(str(child.uuid))
                    nodes.append({"id": str(child.uuid), "name": child.first_name,
                                  "first_surname": child.first_surname, "second_surname": child.second_surname})

                edge = (str(current_uuid), str(child.uuid))
                if edge not in edges_set:
                    edges_set.add(edge)
                    edges.append({"source": str(current_uuid),
                                  "target": str(child.uuid), "type": "parent"})

                if child.uuid not in visited:
                    visited.add(child.uuid)
                    queue.append((child.uuid, level + 1))

        parents = get_parents(session, current_uuid)
        for parent in parents:

            if next_level <= depth:
                if str(parent.uuid) not in nodes_id:
                    nodes_id.add(str(parent.uuid))
                    nodes.append({"id": str(parent.uuid), "name": parent.first_name,
                                  "first_surname": parent.first_surname, "second_surname": parent.second_surname})

                edge = (str(parent.uuid), str(current_uuid))
                if edge not in edges_set:
                    edges_set.add(edge)
                    edges.append({"source": str(parent.uuid), "target": str(
                        current_uuid), "type": "parent"})

                if parent.uuid not in visited:
                    visited.add(parent.uuid)
                    queue.append((parent.uuid, level + 1))

    return data

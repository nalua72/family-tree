import uuid
from fastapi import HTTPException, status

from collections import deque

from sqlalchemy.orm import Session
from app.schemas.persons import PersonResponse
from app.db.base import Person

from app.schemas.relationships import RelationshipType, RelationshipResponse
from app.repositories.person_repository import get_person_by_uuid, get_parents, get_children
from app.utils.person_utils import (
    validate_uuid,
    validate_parent_uuid,
    handle_parent_update,
    map_person_to_response,
)


def get_ancestors_service(session: Session, person_uuid: uuid.UUID) -> list[PersonResponse]:
    """Gets all the ancestors of a person"""

    stack: list[uuid.UUID] = []
    visited: set[uuid.UUID] = set()
    ancestors: list[Person] = []

    parents = get_parents(session, person_uuid)

    for parent in parents:
        stack.append(uuid.UUID(parent.uuid))

    while stack:
        current_uuid = stack.pop()

        if current_uuid in visited:
            continue

        visited.add(current_uuid)

        current = get_person_by_uuid(session, current_uuid)

        if current is None:
            continue

        ancestors.append(current)

        current_parents = get_parents(session, current_uuid)

        for current_parent in current_parents:
            stack.append(uuid.UUID(current_parent.uuid))

    return [map_person_to_response(a) for a in ancestors]


def get_descendants_service(session: Session, person_uuid: uuid.UUID) -> list[PersonResponse]:
    """"Gets all desdendants of a person"""

    stack: list[uuid.UUID] = [person_uuid]
    visited: set[uuid.UUID] = set()
    descendants: list[Person] = []

    if get_person_by_uuid(session, person_uuid) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {person_uuid} no existe"
        )

    while stack:
        current_uuid = stack.pop()

        if current_uuid in visited:
            continue

        visited.add(current_uuid)

        current_children = get_children(session, current_uuid)

        for current_child in current_children:
            current_child_uuid = uuid.UUID(current_child.uuid)

            if current_child_uuid in visited:
                continue
            stack.append(current_child_uuid)
            descendants.append(current_child)

    return [map_person_to_response(d) for d in descendants]


def get_descendants_by_levels_service(session: Session, person_uuid: uuid.UUID) -> list[list[PersonResponse]]:
    """"Gets all desdendants of a person and stores them per level"""

    queue: list[tuple[uuid.UUID, int]] = deque([(person_uuid, 0)])
    visited: set[uuid.UUID] = set()
    descendants: list[list[PersonResponse]] = []

    if get_person_by_uuid(session, person_uuid) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {person_uuid} no existe"
        )

    while queue:
        current_uuid, level = queue.popleft()

        if current_uuid in visited:
            continue

        visited.add(current_uuid)

        # Gets all the children of a person

        current_children = get_children(session, current_uuid)

        for current_child in current_children:

            child_level = level + 1

            current_child_uuid = uuid.UUID(current_child.uuid)

            if current_child_uuid in visited:
                continue

            # Creates a level for a descendant if doesn't exist
            while len(descendants) <= child_level - 1:
                descendants.append([])
            # Stores the descendant in the proper level of the list
            descendants[child_level -
                        1].append(map_person_to_response(current_child))

            queue.append((current_child_uuid, child_level))

    return descendants


def find_relationship_service(session: Session, source_uuid: uuid.UUID, target_uuid: uuid.UUID) -> list[PersonResponse]:
    """Returns a list of uuid of the persons between source_uuid and target_uuid"""

    queue: list[uuid.UUID, list[uuid.UUID]] = deque(
        [(source_uuid, [source_uuid])])
    visited: set[uuid.UUID] = {source_uuid}

    # Source person doesn'exist
    if get_person_by_uuid(session, source_uuid) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {source_uuid} no existe"
        )

    # Target person doesn'exist
    if get_person_by_uuid(session, target_uuid) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {target_uuid} no existe"
        )

    while queue:
        neighbors: list[uuid.UUID] = []

        current_uuid, current_path = queue.popleft()

        # If a connection is found: return the list of Persons in the path of the conenction
        if current_uuid == target_uuid:

            persons_list = [get_person_by_uuid(
                session, node_uuid) for node_uuid in current_path]

            # return a list of the PersonResponse type of the path

            return [map_person_to_response(d) for d in persons_list]

        parents = get_parents(session, current_uuid)
        children = get_children(session, current_uuid)

        for parent in parents:
            neighbors.append(uuid.UUID(parent.uuid))

        for child in children:
            neighbors.append(uuid.UUID(child.uuid))

        # Add to the queue unvisited paths
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = current_path + [neighbor]
                queue.append((neighbor, new_path))

    # If No connection is found raises exception
    raise HTTPException(
        status_code=404,
        detail="No existe relación entre las personas"
    )


def get_relationship_type(session: Session, source_uuid: uuid.UUID, target_uuid: uuid.UUID) -> RelationshipResponse:

    if source_uuid == target_uuid:
        return RelationshipResponse(relationship=RelationshipType.SELF, distance=0)

    path = find_relationship_service(session, source_uuid, target_uuid)
    path_uuids = [node.uuid for node in path]

    movements = get_movements_from_path(session, path_uuids)

    summary = summarize_movements(movements)

    return RelationshipResponse(relationship=map_to_relationship(summary), distance=len(movements))

    # return {map_to_relationship(summary)}


def get_movements_from_path(session: Session, path: list[uuid.UUID]) -> list[int]:
    movements: list[int] = []

    for i in range(len(path) - 1):
        current_uuid = path[i]
        next_uuid = path[i + 1]
        next_uuid_str = str(next_uuid)

        children = get_children(session, current_uuid)
        parents = get_parents(session, current_uuid)

        if any(child.uuid == next_uuid_str for child in children):
            movements.append(-1)
        elif any(parent.uuid == next_uuid_str for parent in parents):
            movements.append(1)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid relationship path: {next_uuid}, {current_uuid} nodes are not directly connected"
            )

    return movements


def summarize_movements(movements: list[int]) -> dict[str, int]:
    n_up = 0
    n_down = 0

    for movement in movements:
        if movement == 1:
            n_up += 1
        else:
            n_down += 1

    summary = {"n_up": n_up, "n_down": n_down}

    return summary


def map_to_relationship(summary: dict[str, int]) -> RelationshipType:
    family_mapping: dict[tuple[int, int], RelationshipType] = {
        (0, 1): RelationshipType.CHILD,
        (0, 2): RelationshipType.GRANDCHILD,
        (1, 0): RelationshipType.PARENT,
        (2, 0): RelationshipType.GRANDPARENT,
        (1, 1): RelationshipType.SIBLING,
        (2, 1): RelationshipType.UNCLE,
        (1, 2): RelationshipType.NEPHEW,
        (2, 2): RelationshipType.COUSIN
    }

    relation: tuple[int, int] = (summary["n_up"], summary["n_down"])

    return family_mapping.get(relation, RelationshipType.DISTANT_RELATIVE)

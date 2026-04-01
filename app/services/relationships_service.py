import uuid
from fastapi import HTTPException, status

from collections import deque

from sqlalchemy.orm import Session
from app.schemas.persons import PersonResponse
from app.db.base import Person

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

    person = session.query(Person).filter(
        Person.uuid == str(person_uuid)).first()

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {person_uuid} no existe"
        )

    if person.father_uuid:
        stack.append(uuid.UUID(person.father_uuid))

    if person.mother_uuid:
        stack.append(uuid.UUID(person.mother_uuid))

    while stack:
        current_uuid = stack.pop()

        if current_uuid in visited:
            continue

        visited.add(current_uuid)

        current = session.query(Person).filter(
            Person.uuid == str(current_uuid)).first()

        if current is None:
            continue

        ancestors.append(current)

        if current.father_uuid:
            stack.append(uuid.UUID(current.father_uuid))

        if current.mother_uuid:
            stack.append(uuid.UUID(current.mother_uuid))

    return [map_person_to_response(a) for a in ancestors]


def get_descendants_service(session: Session, person_uuid: uuid.UUID) -> list[PersonResponse]:
    """"Gets all desdendants of a person"""

    stack: list[uuid.UUID] = [person_uuid]
    visited: set[uuid.UUID] = set()
    descendants: list[Person] = []

    person = session.query(Person).filter(
        Person.uuid == str(person_uuid)).first()

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {person_uuid} no existe"
        )

    while stack:
        current_uuid = stack.pop()

        if current_uuid in visited:
            continue

        visited.add(current_uuid)

        currents = session.query(Person).filter((Person.father_uuid == str(
            current_uuid)) | (Person.mother_uuid == str(current_uuid)))

        for current in currents:
            if current.uuid in visited:
                continue
            descendants.append(current)
            stack.append(current.uuid)

    return [map_person_to_response(d) for d in descendants]


def get_descendants_by_levels_service(session: Session, person_uuid: uuid.UUID) -> list[list[PersonResponse]]:
    """"Gets all desdendants of a person and stores them per level"""

    queue: list[tuple[uuid.UUID, int]] = [(person_uuid, 0)]
    visited: set[uuid.UUID] = set()
    descendants: list[list[PersonResponse]] = []

    person = session.query(Person).filter(
        Person.uuid == str(person_uuid)).first()

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {person_uuid} no existe"
        )

    while queue:
        current_uuid, level = queue.pop(0)

        if current_uuid in visited:
            continue

        visited.add(current_uuid)

        # Gets all the children of a person
        currents = session.query(Person).filter((Person.father_uuid == str(
            current_uuid)) | (Person.mother_uuid == str(current_uuid)))

        for current in currents:

            child_level = level + 1

            if current.uuid in visited:
                continue
            # Creates a level for a descendant if doesn't exist
            while len(descendants) <= child_level - 1:
                descendants.append([])
            # Stores the descendant in the proper level of the list
            descendants[child_level -
                        1].append(map_person_to_response(current))

            queue.append((current.uuid, child_level))

    return descendants


def find_relationship_service(session: Session, source_uuid: uuid.UUID, target_uuid: uuid.UUID) -> list[PersonResponse]:
    """Returns a list of uuid of the persons between source_uuid and target_uuid"""

    queue = deque([(source_uuid, [source_uuid])])
    visited = {source_uuid}

    source_person = session.query(Person).filter(
        Person.uuid == str(source_uuid)).first()

    # Source person doesn'exist
    if source_person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {source_uuid} no existe"
        )

    target_person = session.query(Person).filter(
        Person.uuid == str(target_uuid)).first()

    # Source person doesn'exist
    if target_person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {target_uuid} no existe"
        )

    while queue:
        neighbors: list[uuid.UUID] = []

        current_uuid, current_path = queue.popleft()

        # If a connection is found: return the list of Persons in the path of the conenction
        if current_uuid == target_uuid:

            uuid_list_str = [str(u) for u in current_path]
            persons_list = session.query(Person).filter(
                Person.uuid.in_(uuid_list_str)).all()

            persons_dict = {}
            for person in persons_list:
                persons_dict[person.uuid] = person

            persons_list_ordered = [persons_dict[str(k)] for k in current_path]

            # return a list of the PersonResponse type of the path

            return [map_person_to_response(d) for d in persons_list_ordered]

        current_person = session.query(Person).filter(
            Person.uuid == str(current_uuid)).first()

        # Gets neigbors: Father, Mother and all children
        if current_person.father_uuid:
            neighbors.append(uuid.UUID(current_person.father_uuid))

        if current_person.mother_uuid:
            neighbors.append(uuid.UUID(current_person.mother_uuid))

        children = session.query(Person).filter((Person.father_uuid == str(
            current_uuid)) | (Person.mother_uuid == str(current_uuid)))

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

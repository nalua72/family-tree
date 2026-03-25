
import uuid
from app.db.base import Person, SessionLocal
from app.schemas.persons import PersonResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


def map_person_to_response(person: Person) -> PersonResponse:
    """"Maps the value sin the database with the Response schema"""

    return PersonResponse(
        uuid=uuid.UUID(person.uuid),
        first_name=person.first_name,
        first_surname=person.first_surname,
        second_surname=person.second_surname,
        date_of_birth=person.date_of_birth,
        date_of_death=person.date_of_death,
        city_of_birth=person.city_of_birth,
        province_of_birth=person.province_of_birth,
        country_of_birth=person.country_of_birth,
        gender=person.gender,
        marital_status=person.marital_status,
        biography=person.biography,
        notes=person.notes,
        nickname=person.nickname,
        photo_url=person.photo_url,
        external_reference=person.external_reference,
        father_uuid=uuid.UUID(
            person.father_uuid) if person.father_uuid else None,
        mother_uuid=uuid.UUID(
            person.mother_uuid) if person.mother_uuid else None,
        birth_order=person.birth_order
    )


def validate_uuid(uuid_str: str) -> uuid.UUID:
    """Checks if an uuid is valid"""
    try:
        return uuid.UUID(uuid_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UUID inválido"
        ) from exc


def validate_parent_uuid(uuid_value: uuid.UUID, session: Session) -> Person:
    """Checks the validity of the parent uuid. Returns the parent if valid"""
    parent = session.query(Person).filter(
        Person.uuid == str(uuid_value)).first()

    if parent is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No existe una persona con ese UUID"
        )

    return parent


def ensure_no_cycle(session: Session, source_uuid: uuid.UUID, target_uuid: uuid.UUID) -> None:
    """Function checks that an user can't be the parent of one of his/her ancestors.
       Performs a DFS traversal to ensure that assigning target_uuid as a parent of source_uuid does not create a cycle.
    """

    stack: list[uuid.UUID] = [target_uuid]
    visited: set[uuid.UUID] = set()

    while stack:
        current_uuid = stack.pop()

        if current_uuid in visited:
            continue

        visited.add(current_uuid)

        if current_uuid == source_uuid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="No se puede crear un ciclo en el árbol genealógico")

        current = session.query(Person).filter(
            Person.uuid == str(current_uuid)).first()

        if current is None:
            continue

        if current.father_uuid:
            stack.append(uuid.UUID(current.father_uuid))

        if current.mother_uuid:
            stack.append(uuid.UUID(current.mother_uuid))


def handle_parent_update(session: Session, person_db: Person, field: str, value: uuid.UUID | None, source_uuid: uuid.UUID) -> None:
    """Manages inconsitencies in the graph regarding father and mother uuid"""

    if value is None:
        setattr(person_db, field, None)
    elif value == source_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Una persona no puede ser progenitora de si misma"
        )
    else:
        parent = validate_parent_uuid(value, session)
        ensure_no_cycle(session, source_uuid, value)
        setattr(person_db, field, str(parent.uuid))

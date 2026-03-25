import uuid
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from app.schemas.persons import PersonCreate, PersonUpdate, PersonResponse
from app.db.base import Person

from app.utils.person_utils import (
    validate_uuid,
    validate_parent_uuid,
    handle_parent_update,
    map_person_to_response,
)


def get_persons_service(session: Session) -> list[PersonResponse]:
    """Gets the value of all persons"""

    persons = session.query(Person).all()

    return [map_person_to_response(p) for p in persons]


def get_person_by_id_service(session: Session, uuid_str: str) -> PersonResponse:
    """Gets the values of a person by his uuid"""

    uuid_obj = validate_uuid(uuid_str)

    person = session.query(Person).filter(
        Person.uuid == str(uuid_obj)).first()

    if person is None:
        # Raise exception 404 Not Found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {uuid_str} no existe"
        )

    return map_person_to_response(person)


def create_person_service(session: Session, person: PersonCreate) -> PersonResponse:
    """Adds a new person to the database"""
    new_uuid = uuid.uuid4()
    father_uuid_str = mother_uuid_str = None

    if person.father_uuid is not None:
        validate_parent_uuid(person.father_uuid, session)
        father_uuid_str = str(person.father_uuid)

    if person.mother_uuid is not None:
        validate_parent_uuid(person.mother_uuid, session)
        mother_uuid_str = str(person.mother_uuid)

    person_db = Person(
        uuid=str(new_uuid),
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
        father_uuid=father_uuid_str,
        mother_uuid=mother_uuid_str,
        birth_order=person.birth_order
    )

    session.add(person_db)
    session.commit()
    session.refresh(person_db)

    return map_person_to_response(person_db)


def update_person_service(session: Session, uuid_str: str, person: PersonUpdate) -> PersonResponse:
    """Updates values of the selected fields of a person"""

    uuid_obj = validate_uuid(uuid_str)

    person_db = session.query(Person).filter(
        Person.uuid == str(uuid_obj)).first()

    if person_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {uuid_str} no existe"
        )

    # Only will keep those fields with data
    update_data = person.model_dump(exclude_unset=True)

    for field, value in update_data.items():

        # The case of the uuid of the father and mother are special cases so they are treated separetely
        if field in {"father_uuid", "mother_uuid"}:
            handle_parent_update(session, person_db, field, value, uuid_obj)

        else:
            # Maps the desired values of the person to the database
            setattr(person_db, field, value)

    session.commit()
    session.refresh(person_db)

    return map_person_to_response(person_db)


def delete_person_service(session: Session, uuid_str: str) -> dict[str, str]:
    """Manages the process of deleting a person using his/her uuid from the database"""

    uuid_obj = validate_uuid(uuid_str)

    person = session.query(Person).filter(
        Person.uuid == str(uuid_obj)).first()

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La persona con UUID {uuid_str} no existe"
        )

    # Check if he/she is father or mother or someone
    has_children = session.query(Person).filter(
        (Person.father_uuid == str(uuid_obj)) |
        (Person.mother_uuid == str(uuid_obj))
    ).first()

    # Can'be deleted
    if has_children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede borrar una persona que tiene hijos"
        )

    session.delete(person)
    session.commit()

    return {"detail": "Persona eliminada correctamente"}

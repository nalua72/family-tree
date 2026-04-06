import uuid

from sqlalchemy.orm import Session
from app.db.base import Person


def get_person_by_uuid(session: Session, uuid: uuid.UUID) -> Person | None:

    return session.query(Person).filter(Person.uuid == str(uuid)).first()


def get_all_persons(session: Session) -> list[Person]:

    return session.query(Person).all()


def get_parents(session: Session, uuid: uuid.UUID) -> list[Person]:
    parents: list[Person] = []

    person = session.query(Person).filter(Person.uuid == str(uuid)).first()

    if not person:
        return []

    if person.father_uuid:
        father = session.query(Person).filter(
            Person.uuid == str(person.father_uuid)).first()
        if father:
            parents.append(father)
    if person.mother_uuid:
        mother = session.query(Person).filter(
            Person.uuid == str(person.mother_uuid)).first()
        if mother:
            parents.append(mother)

    return parents


def get_children(session: Session, uuid: uuid.UUID) -> list[Person]:

    return session.query(Person).filter(
        (Person.father_uuid == str(uuid)) | (Person.mother_uuid == str(uuid))).all()


def save_person(session: Session, person: Person) -> Person:

    session.add(person)
    session.commit()
    session.refresh(person)

    return person


def update_person(session: Session, person: Person) -> Person:

    session.commit()
    session.refresh(person)

    return person


def delete_person(session: Session, person: Person):

    session.delete(person)
    session.commit()

import uuid

from app.schemas.persons import PersonCreate, PersonResponse

persons: list[dict] = [
    {
        "uuid": uuid.uuid4(),
        "name": "José Manuel Rodríguez Pérez",
        "date_of_birth": "1972-07-10",
        "date_of_death": None
    },
    {
        "uuid": uuid.uuid4(),
        "name": "Isabel Vara Moreno",
        "date_of_birth": "1970-10-06",
        "date_of_death": None
    },
    {
        "uuid": uuid.uuid4(),
        "name": "Saúl Rodríguez Vara",
        "date_of_birth": "2010-10-17",
        "date_of_death": None
    }
]


def get_persons_service() -> list[PersonResponse]:
    return [PersonResponse(**person) for person in persons]


def create_person_service(person: PersonCreate) -> PersonResponse:
    new_uuid = uuid.uuid4()
    new_person = {
        "uuid": new_uuid,
        "name": person.name,
        "date_of_birth": person.date_of_birth,
        "date_of_death": person.date_of_death,
    }

    persons.append(new_person)
    return PersonResponse(**new_person)

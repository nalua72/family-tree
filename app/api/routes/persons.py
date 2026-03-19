import uuid

from app.schemas.persons import PersonCreate, PersonResponse

from fastapi import APIRouter

router = APIRouter()

persons: list[PersonResponse] = [
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


@router.get("/persons", response_model=list[PersonResponse])
def get_persons():
    return persons


@router.post("/persons", response_model=PersonResponse)
def create_person(person: PersonCreate):
    new_uuid = uuid.uuid4()
    new_person = {
        "uuid": new_uuid,
        "name": person.name,
        "date_of_birth": person.date_of_birth,
        "date_of_death": person.date_of_death,
    }

    persons.append(new_person)
    return new_person

from app.schemas.persons import PersonCreate, PersonUpdate, PersonResponse
from app.services.person_service import get_persons_service, get_person_by_id_service, create_person_service, update_person_service, delete_person_service, validate_uuid
import uuid
from fastapi import HTTPException, status
from fastapi import APIRouter

router = APIRouter()

# Endpoint to get all persons


@router.get("/persons", response_model=list[PersonResponse])
def get_persons():
    return get_persons_service()

# Endpoint to get a person by uuid


@router.get("/persons/{uuid_str}", response_model=PersonResponse)
def get_person_by_id(uuid_str: str):

    validate_uuid(uuid_str)  # HTTPException if uuid is invalid

    return get_person_by_id_service(uuid_str)

# Endpoint to get add a person


@router.post("/persons", response_model=PersonResponse)
def create_person(person: PersonCreate):
    return create_person_service(person)

# Endpoint to update a person


@router.patch("/persons/{uuid_str}", response_model=PersonResponse)
def update_person(uuid_str: str, person: PersonUpdate):

    validate_uuid(uuid_str)  # HTTPException if uuid is invalid

    return update_person_service(uuid_str, person)

# Endpoint to delete a person


@router.post("/persons/{uuid_str}", response_model=PersonResponse)
def delete_person(uuid_str: str):

    validate_uuid(uuid_str)  # HTTPException if uuid is invalid

    return delete_person_service(uuid_str)

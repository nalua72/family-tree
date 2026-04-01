from app.db.sessions import get_db
from app.schemas.persons import PersonCreate, PersonUpdate, PersonResponse
from app.services.person_service import (get_persons_service,
                                         get_person_by_id_service,
                                         create_person_service,
                                         update_person_service,
                                         delete_person_service,
                                         validate_uuid
                                         )

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends


router = APIRouter()

# Endpoint to get all persons


@router.get("/persons", response_model=list[PersonResponse])
def get_persons(session: Session = Depends(get_db)):
    return get_persons_service(session)

# Endpoint to get a person by uuid


@router.get("/persons/{uuid_str}", response_model=PersonResponse)
def get_person_by_id(uuid_str: str, session: Session = Depends(get_db)):

    validate_uuid(uuid_str)  # HTTPException if uuid is invalid

    return get_person_by_id_service(session, uuid_str)

# Endpoint to get add a person


@router.post("/persons", response_model=PersonResponse)
def create_person(person: PersonCreate, session: Session = Depends(get_db)):
    return create_person_service(session, person)

# Endpoint to update a person


@router.patch("/persons/{uuid_str}", response_model=PersonResponse)
def update_person(uuid_str: str, person: PersonUpdate, session: Session = Depends(get_db)):

    validate_uuid(uuid_str)  # HTTPException if uuid is invalid

    return update_person_service(session, uuid_str, person)

# Endpoint to delete a person


@router.post("/persons/{uuid_str}", response_model=PersonResponse)
def delete_person(uuid_str: str, session: Session = Depends(get_db)):

    validate_uuid(uuid_str)  # HTTPException if uuid is invalid

    return delete_person_service(session, uuid_str)

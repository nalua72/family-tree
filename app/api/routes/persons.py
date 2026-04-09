from app.db.sessions import get_db
from app.schemas.errors import ErrorResponse
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


@router.get("/persons",
            response_model=list[PersonResponse],
            summary="Get all persons",
            description="Return all the persons in the database"
            )
def get_persons(session: Session = Depends(get_db)):
    return get_persons_service(session)

# Endpoint to get a person by uuid


@router.get("/persons/{person_uuid_str}",
            response_model=PersonResponse,
            responses={
                400: {
                    "model": ErrorResponse,
                    "description": "Invalid UUID format or invalid relationship path"
                },
                404: {
                    "model": ErrorResponse,
                    "description": "Person not found"
                }
            },
            summary="Get a person by their UUID",
            description="Return a person by their UUID"
            )
def get_person(person_uuid_str: str, session: Session = Depends(get_db)):

    # HTTPException if uuid is invalid
    person_uuid = validate_uuid(person_uuid_str)

    return get_person_by_id_service(session, person_uuid)

# Endpoint to get add a person


@router.post("/persons",
             status_code=201,
             response_model=PersonResponse,
             responses={
                 400: {
                     "model": ErrorResponse,
                     "description": "Invalid UUID format or invalid relationship path"
                 }
             },
             summary="Create a new person",
             description="Create a new person"
             )
def create_person(person: PersonCreate, session: Session = Depends(get_db)):
    return create_person_service(session, person)

# Endpoint to update a person


@router.patch("/persons/{person_uuid_str}",
              response_model=PersonResponse,
              responses={
                  400: {
                      "model": ErrorResponse,
                      "description": "Invalid UUID format or invalid relationship path"
                  },
                  404: {
                      "model": ErrorResponse,
                      "description": "Person not found"
                  }
              },
              summary="Update the data of a person",
              description="Update the data of a person"
              )
def update_person(person_uuid_str: str, person: PersonUpdate, session: Session = Depends(get_db)):

    # HTTPException if uuid is invalid
    person_uuid = validate_uuid(person_uuid_str)

    return update_person_service(session, person_uuid, person)

# Endpoint to delete a person


@router.delete("/persons/{person_uuid_str}",
               response_model=ErrorResponse,
               responses={
                   400: {
                       "model": ErrorResponse,
                       "description": "Invalid UUID format or invalid relationship path"
                   },
                   404: {
                       "model": ErrorResponse,
                       "description": "Person not found"
                   }
               },
               summary="Delete a person",
               description="Delete a person")
def delete_person(person_uuid_str: str, session: Session = Depends(get_db)):

    # HTTPException if uuid is invalid
    person_uuid = validate_uuid(person_uuid_str)

    return delete_person_service(session, person_uuid)

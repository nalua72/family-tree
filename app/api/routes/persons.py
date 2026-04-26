from app.db.sessions import get_db
from app.schemas.errors import ErrorResponse
from app.schemas.persons import PersonCreate, PersonUpdate, PersonResponse
from app.schemas.tree import PersonTreeResponse
from app.services.person_service import (get_persons_service,
                                         get_person_by_id_service,
                                         create_person_service,
                                         update_person_service,
                                         delete_person_service,
                                         validate_uuid
                                         )
from app.services.tree_service import get_person_tree_service

from sqlalchemy.orm import Session
from fastapi import APIRouter, Query, Depends
from typing import Annotated


router = APIRouter(prefix="/persons", tags=["persons"])

# Endpoint to get all persons


@router.get("/",
            response_model=list[PersonResponse],
            summary="Get all persons",
            description="Return all the persons in the database"
            )
def get_persons(session: Session = Depends(get_db)) -> list[PersonResponse]:
    return get_persons_service(session)

# Endpoint to get a person by uuid


@router.get("/{person_uuid_str}",
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
def get_person(person_uuid_str: str, session: Session = Depends(get_db)) -> PersonResponse:

    # HTTPException if uuid is invalid
    person_uuid = validate_uuid(person_uuid_str)

    return get_person_by_id_service(session, person_uuid)

# Endpoint to get add a person


@router.post("/",
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
def create_person(person: PersonCreate, session: Session = Depends(get_db)) -> PersonResponse:
    return create_person_service(session, person)

# Endpoint to update a person


@router.patch("/{person_uuid_str}",
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
def update_person(person_uuid_str: str, person: PersonUpdate, session: Session = Depends(get_db)) -> PersonResponse:

    # HTTPException if uuid is invalid
    person_uuid = validate_uuid(person_uuid_str)

    return update_person_service(session, person_uuid, person)

# Endpoint to delete a person


@router.delete("/{person_uuid_str}",
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


@router.get("/{person_uuid_str}/tree",
            response_model=PersonTreeResponse,
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
            summary="Get a person's family tree",
            description="""
            Return a person's family tree up to the specified depth.

            The response includes the requested person as the root node, plus all reachable
            relatives within the given number of relationship steps.

            Relationships are always returned in stable parent-to-child direction:
            - `source` is the parent
            - `target` is the child
            - `type` is always `"parent"`

            Use the `depth` query parameter to control how many relationship levels are included:
            - `0` returns only the root person
            - `1` includes direct parents and children
            - `2` includes second-level relatives"""
            )
def get_person_tree(person_uuid_str: str, depth: Annotated[int, Query(ge=0)] = 1, session: Session = Depends(get_db)) -> PersonTreeResponse:

    # HTTPException if uuid is invalid
    person_uuid = validate_uuid(person_uuid_str)

    return get_person_tree_service(session, person_uuid, depth)

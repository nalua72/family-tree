import uuid
from app.db.sessions import get_db
from app.services.person_service import validate_uuid
from app.services.relationships_service import (get_ancestors_service,
                                                get_descendants_service,
                                                get_descendants_by_levels_service,
                                                find_relationship_service,
                                                get_relationship_type
                                                )
from app.schemas.errors import ErrorResponse
from app.schemas.persons import PersonResponse
from app.schemas.relationships import RelationshipResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/relationships", tags=["relationships"])

# Endpoint to get all ancestors from a user person


@router.get("/{person_uuid_str}/ancestors",
            response_model=list[PersonResponse],
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
            summary="Get ancestors of a person",
            description="Returns all ancestors of a person, including parents, grandparents and further generations.")
def get_ancestors(person_uuid_str: str, session: Session = Depends(get_db)):

    person_uuid = validate_uuid(person_uuid_str)

    return get_ancestors_service(session, person_uuid)

# Endpoint to get all descendants from a user person


@router.get("/{person_uuid_str}/descendants",
            response_model=list[PersonResponse],
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
            summary="Get descendants of a person",
            description="Returns all descendants of a person, including children, grandchildren and further generations.")
def get_descendants(person_uuid_str: str, session: Session = Depends(get_db)):

    person_uuid = validate_uuid(person_uuid_str)

    return get_descendants_service(session, person_uuid)


@router.get("/{person_uuid_str}/descendants-by-level",
            response_model=list[list[PersonResponse]],
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
            summary="Get descendants grouped by generation",
            description="Returns descendants grouped by levels. Each inner list represents one generation level.")
def get_descendants_by_level(person_uuid_str: str, session: Session = Depends(get_db)):

    person_uuid = validate_uuid(person_uuid_str)

    return get_descendants_by_levels_service(session, person_uuid)

# Endpoint to get the shortest relationship path between 2 persons


@router.get("/{person_source_uuid_str}/path/{person_target_uuid_str}",
            response_model=list[PersonResponse],
            responses={
                400: {
                    "model": ErrorResponse,
                    "description": "Invalid UUID format or invalid relationship path"
                },
                404: {
                    "model": ErrorResponse,
                    "description": "Person not found or no relationship exists"
                }
            },
            summary="Find relationship path between two persons",
            description="Returns the shortest relationship path between two persons, including both source and target.")
def find_relationship(person_source_uuid_str: str, person_target_uuid_str: str, session: Session = Depends(get_db)):

    person_source_uuid = validate_uuid(person_source_uuid_str)
    person_target_uuid = validate_uuid(person_target_uuid_str)

    return find_relationship_service(session, person_source_uuid, person_target_uuid)

# Endpoint to get the relationship type between 2 persons and their distance


@router.get("/{person_source_uuid_str}/relationship/{person_target_uuid_str}",
            response_model=RelationshipResponse,
            responses={
                400: {
                    "model": ErrorResponse,
                    "description": "Invalid UUID format or invalid relationship path"
                },
                404: {
                    "model": ErrorResponse,
                    "description": "Person not found or no relationship exists"
                }
            },
            summary="Get relationship type between two person including their distance",
            description="Returns the relationship type (e.g., PARENT, CHILD, SIBLING, COUSIN) and the distance between two persons")
def get_relationship_type_endpoint(person_source_uuid_str: str, person_target_uuid_str: str, session: Session = Depends(get_db)):

    person_source_uuid = validate_uuid(person_source_uuid_str)
    person_target_uuid = validate_uuid(person_target_uuid_str)

    return get_relationship_type(session, person_source_uuid, person_target_uuid)

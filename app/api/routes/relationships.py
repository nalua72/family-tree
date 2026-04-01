import uuid
from app.db.sessions import get_db

from app.services.relationships_service import (get_ancestors_service,
                                                get_descendants_service,
                                                get_descendants_by_levels_service,
                                                find_relationship_service
                                                )
from app.schemas.persons import PersonResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/relationships", tags=["relationships"])

# Endpoint to get all ancestors from a user person


@router.get("/{person_uuid}/ancestors", response_model=list[PersonResponse],
            summary="Get ancestors of a person",
            description="Returns all ancestors of a person, including parents, grandparents and further generations.")
def get_ancestors(person_uuid: uuid.UUID, session: Session = Depends(get_db)):
    return get_ancestors_service(session, person_uuid)

# Endpoint to get all descendants from a user person


@router.get("/{person_uuid}/descendants", response_model=list[PersonResponse],
            summary="Get descendants of a person",
            description="Returns all ancestors of a person, including children, grandchildren and further generations.")
def get_descendants(person_uuid: uuid.UUID, session: Session = Depends(get_db)):
    return get_descendants_service(session, person_uuid)


@router.get("/{person_uuid}/descendants_by_level", response_model=list[list[PersonResponse]],
            summary="Get descendants grouped by generation",
            description="Returns descendants grouped by levels. Each inner list represents one generation level.")
def get_descendants_by_level(person_uuid: uuid.UUID, session: Session = Depends(get_db)):
    return get_descendants_by_levels_service(session, person_uuid)

# Endpoint to get the shortest relationship path between 2 persons


@router.get("/{person_source_uuid}/to/{person_target_uuid}", response_model=list[PersonResponse],
            summary="Find relationship path between two persons",
            description="Returns the shortest relationship path between two persons, including both source and target.")
def find_relationship(person_source_uuid: uuid.UUID, person_target_uuid: uuid.UUID, session: Session = Depends(get_db)):
    return find_relationship_service(session, person_source_uuid, person_target_uuid)

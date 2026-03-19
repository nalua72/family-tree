from app.schemas.persons import PersonCreate, PersonResponse
from app.services.person_service import get_persons_service, create_person_service

from fastapi import APIRouter

router = APIRouter()


@router.get("/persons", response_model=list[PersonResponse])
def get_persons():
    return get_persons_service()


@router.post("/persons", response_model=PersonResponse)
def create_person(person: PersonCreate):
    return create_person_service(person)

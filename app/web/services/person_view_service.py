import uuid
from app.schemas.persons import PersonDetailView
from app.services.person_service import get_person_by_id_service
from app.services.relationships_service import get_descendants_by_levels_service

from sqlalchemy.orm import Session


def build_person_view_data(person_uuid: uuid.UUID, session: Session) -> PersonDetailView:

    person = get_person_by_id_service(session=session, person_uuid=person_uuid)
    descendants = get_descendants_by_levels_service(
        session=session, person_uuid=person_uuid)

    person_children = descendants[0] if descendants else []

    return PersonDetailView(uuid=str(person_uuid), first_name=person.first_name, first_surname=person.first_surname, second_surname=person.second_surname,
                            city_of_birth=person.city_of_birth, date_of_birth=person.date_of_birth, date_of_death=person.date_of_death, children=person_children)


"""     person_view_data = {
        "uuid": str(person_uuid),
        "name": person.first_name,
        "first_surname": person.first_surname,
        "second_surname": person.second_surname,
        "place_of_birth": person.city_of_birth,
        "date_of_birth": person.date_of_birth,
        "place_of_death": person.city_of_death,
        "date_of_death": person.date_of_death,
        "children": person_children
    } """

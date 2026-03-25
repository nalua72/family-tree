import pytest
import uuid
from app.db.base import Person
from sqlalchemy.orm import Session
from app.schemas.persons import PersonCreate, PersonUpdate
from app.services.person_service import get_persons_service, get_person_by_id_service, create_person_service, update_person_service, delete_person_service
from app.utils.person_utils import ensure_no_cycle
from fastapi import HTTPException


def test_ensure_no_cycle_happy_path(session):
    """
    Should NOT raise an exception when assigning a parent
    that does not create a cycle.
    """

    # ARRANGE → create two independent persons
    person_a = create_person_service(session, PersonCreate(
        first_name="Name1",
        first_surname="Surname1",
        second_surname="One"
    ))

    person_b = create_person_service(session, PersonCreate(
        first_name="Name2",
        first_surname="Surname2",
        second_surname="Two"
    ))

    # ACT & ASSERT → no exception should be raised
    ensure_no_cycle(session, person_a.uuid, person_b.uuid)


def test_ensure_no_cycle_direct_cycle(session):
    """
    Should raise an exception when assigning a parent
    that DOES create a cycle.
    """

    # ARRANGE -> A -> B
    person_a = create_person_service(session, PersonCreate(
        first_name="Name1",
        first_surname="Surname1",
        second_surname="One"
    ))

    person_b = create_person_service(session, PersonCreate(
        first_name="Name2",
        first_surname="Surname2",
        second_surname="Two",
        father_uuid=person_a.uuid
    ))

    # ACT + Assert -> trying to make A child of B (cycle)

    with pytest.raises(HTTPException) as exc:
        ensure_no_cycle(session, person_a.uuid, person_b.uuid)

    assert exc.value.status_code == 400
    assert "ciclo" in exc.value.detail.lower()


def test_ensure_no_cycle_indirect_cycle(session):
    """
    Should raise an exception when assigning a grandparent
    that DOES create a cycle.
    """

    # ARRANGE -> A -> B -> C
    person_a = create_person_service(session, PersonCreate(
        first_name="Name1",
        first_surname="Surname1",
        second_surname="One"
    ))

    person_b = create_person_service(session, PersonCreate(
        first_name="Name2",
        first_surname="Surname2",
        second_surname="Two",
        father_uuid=person_a.uuid
    ))

    person_c = create_person_service(session, PersonCreate(
        first_name="Name3",
        first_surname="Surname3",
        second_surname="Three",
        father_uuid=person_b.uuid
    ))

    # ACT + Assert -> trying to make A <- C (cycle)

    with pytest.raises(HTTPException) as exc:
        ensure_no_cycle(session, person_a.uuid, person_c.uuid)

    assert exc.value.status_code == 400
    assert "ciclo" in exc.value.detail.lower()


def test_ensure_no_cycle_mother_branch(session):
    """
    Should raise an exception when assigning a grandparent
    that DOES create a cycle.
    """

    # ARRANGE → A → B (father), B → C (mother)
    person_a = create_person_service(session, PersonCreate(
        first_name="Name1",
        first_surname="Surname1",
        second_surname="One"
    ))

    person_b = create_person_service(session, PersonCreate(
        first_name="Name2",
        first_surname="Surname2",
        second_surname="Two",
        father_uuid=person_a.uuid
    ))

    person_c = create_person_service(session, PersonCreate(
        first_name="Name3",
        first_surname="Surname3",
        second_surname="Three",
        mother_uuid=person_b.uuid
    ))

    # ACT + Assert -> trying to make A <- C (cycle)

    with pytest.raises(HTTPException) as exc:
        ensure_no_cycle(session, person_a.uuid, person_c.uuid)

    assert exc.value.status_code == 400
    assert "ciclo" in exc.value.detail.lower()


def test_ensure_no_cycle_with_shared_ancestor(session):
    """
    Should raise an exception when assigning a parent
    that creates a cycle through multiple ancestor paths.
    """

    # ARRANGE → B -> A (father), C -> A (mother), D -> B (father) + C (mother)
    person_a = create_person_service(session, PersonCreate(
        first_name="Name1",
        first_surname="Surname1",
        second_surname="One"
    ))

    person_b = create_person_service(session, PersonCreate(
        first_name="Name2",
        first_surname="Surname2",
        second_surname="Two",
        father_uuid=person_a.uuid
    ))

    person_c = create_person_service(session, PersonCreate(
        first_name="Name3",
        first_surname="Surname3",
        second_surname="Three",
        mother_uuid=person_a.uuid
    ))

    person_d = create_person_service(session, PersonCreate(
        first_name="Name4",
        first_surname="Surname4",
        second_surname="Four",
        father_uuid=person_b.uuid,
        mother_uuid=person_c.uuid
    ))

    # ACT + Assert -> trying to make A <- D (cycle)

    with pytest.raises(HTTPException) as exc:
        ensure_no_cycle(session, person_a.uuid, person_d.uuid)

    assert exc.value.status_code == 400
    assert "ciclo" in exc.value.detail.lower()

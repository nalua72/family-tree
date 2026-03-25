import pytest
import uuid
from fastapi import HTTPException

from app.schemas.persons import PersonCreate, PersonUpdate
from app.services.person_service import get_persons_service, get_person_by_id_service, create_person_service, update_person_service, delete_person_service
from app.db.base import Person


# CREATE TESTS


def test_create_person_success(session):
    # ARRANGE
    person_data = PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    )

    # ACT
    result = create_person_service(session, person_data)

    # ASSERT
    assert result.uuid is not None
    assert result.first_name == "Juan"
    assert result.first_surname == "Perez"
    assert result.second_surname == "Gomez"

    # DB check
    db_person = session.query(Person).filter(
        Person.uuid == str(result.uuid)
    ).first()

    assert db_person is not None
    assert str(result.uuid) == db_person.uuid
    assert db_person.first_name == "Juan"


def test_create_person_with_father(session):

    father = create_person_service(session, PersonCreate(
        first_name="Padre",
        first_surname="Perez",
        second_surname="Uno"
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Dos",
        father_uuid=father.uuid
    ))

    assert child.father_uuid == father.uuid


def test_create_person_with_mother(session):

    mother = create_person_service(session, PersonCreate(
        first_name="Madre",
        first_surname="Perez",
        second_surname="Uno"
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Dos",
        mother_uuid=mother.uuid
    ))

    assert child.mother_uuid == mother.uuid


def test_create_person_with_both_parents(session):

    father = create_person_service(session, PersonCreate(
        first_name="Padre",
        first_surname="Perez",
        second_surname="Uno"
    ))

    mother = create_person_service(session, PersonCreate(
        first_name="Madre",
        first_surname="Perez",
        second_surname="Dos"
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Tres",
        father_uuid=father.uuid,
        mother_uuid=mother.uuid
    ))

    assert child.father_uuid == father.uuid
    assert child.mother_uuid == mother.uuid


def test_create_person_invalid_father(session):

    with pytest.raises(HTTPException) as exc:
        create_person_service(session, PersonCreate(
            first_name="Hijo",
            first_surname="Perez",
            second_surname="Dos",
            father_uuid=uuid.uuid4()
        ))

    assert exc.value.status_code == 400


def test_create_person_invalid_mother(session):

    with pytest.raises(HTTPException) as exc:
        create_person_service(session, PersonCreate(
            first_name="Hijo",
            first_surname="Perez",
            second_surname="Dos",
            mother_uuid=uuid.uuid4()
        ))

    assert exc.value.status_code == 400


def test_create_person_self_parent(session):

    fake_uuid = uuid.uuid4()

    with pytest.raises(HTTPException) as exc:
        create_person_service(session, PersonCreate(
            first_name="Juan",
            first_surname="Perez",
            second_surname="Gomez",
            father_uuid=fake_uuid  # simular self (si tu lógica lo detecta)
        ))

    assert exc.value.status_code == 400


# UPDATE TESTS


def test_update_person_partial(session):

    # ARRANGE

    person_data = PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    )

    created = create_person_service(session, person_data)

    person_update = PersonUpdate(
        biography="User biography update"
    )

    # ACT

    updated = update_person_service(
        session, str(created.uuid), person_update)

    # ASSERT

    # Updated field
    assert updated.biography == "User biography update"

    # Not updated fields
    assert updated.first_name == "Juan"
    assert updated.first_surname == "Perez"
    assert updated.second_surname == "Gomez"

    # DB check
    db_person = session.query(Person).filter(
        Person.uuid == str(created.uuid)
    ).first()

    assert db_person is not None
    assert db_person.biography == "User biography update"


def test_update_person_invalid_father(session):

    # ARRANGE

    person_data = PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    )

    created = create_person_service(session, person_data)

    invalid_uuid = uuid.uuid4()

    person_update = PersonUpdate(
        father_uuid=invalid_uuid
    )

    # ACT + ASSERT (expect error)

    with pytest.raises(HTTPException) as exc:
        update_person_service(
            session, str(created.uuid), person_update
        )

    assert exc.value.status_code == 400

    # ASSERT check: DB has not changed

    db_person = session.query(Person).filter(
        Person.uuid == str(created.uuid)
    ).first()

    assert db_person is not None
    assert db_person.father_uuid is None


def test_update_person_remove_father_success(session):

    # ARRANGE

    father_data = PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    )

    father_created = create_person_service(session, father_data)

    child_data = PersonCreate(
        first_name="Pedro",
        first_surname="Perez",
        second_surname="García",
        father_uuid=father_created.uuid
    )

    child_created = create_person_service(session, child_data)

    # ACT → deletes father
    update_data = PersonUpdate(
        father_uuid=None
    )

    child_updated = update_person_service(
        session,
        str(child_created.uuid),
        update_data
    )

    # ASSERT

    # in schema
    assert child_updated.first_name == "Pedro"
    assert child_updated.father_uuid is None

    # in DB
    db_child = session.query(Person).filter(
        Person.uuid == str(child_created.uuid)
    ).first()

    assert db_child is not None
    assert db_child.uuid == str(child_created.uuid)
    assert db_child.father_uuid is None

    # other fields don't change
    assert db_child.first_name == "Pedro"


def test_update_person_remove_mother_success(session):

    # ARRANGE
    mother = create_person_service(session, PersonCreate(
        first_name="Madre",
        first_surname="Perez",
        second_surname="Uno"
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Dos",
        mother_uuid=mother.uuid
    ))

    # ACT
    updated = update_person_service(
        session,
        str(child.uuid),
        PersonUpdate(mother_uuid=None)
    )

    # ASSERT
    assert updated.mother_uuid is None


def test_update_person_self_parent(session):

    # ARRANGE

    person_data = PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    )

    person_created = create_person_service(session, person_data)

    # ACT → updates person father uuid with its own uuid
    update_data = PersonUpdate(
        father_uuid=person_created.uuid
    )

    # ASSERT → error expected
    with pytest.raises(HTTPException) as exc:
        update_person_service(
            session,
            str(person_created.uuid),
            update_data
        )

    assert exc.value.status_code == 400

    # ASSERT check: DB has not changed
    db_person = session.query(Person).filter(
        Person.uuid == str(person_created.uuid)
    ).first()

    assert db_person is not None
    assert db_person.father_uuid is None


def test_update_person_cycle_father_branch(session):

    # ARRANGE

    grandparent_data = PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    )
    grandparent_created = create_person_service(session, grandparent_data)

    parent_data = PersonCreate(
        first_name="Pedro",
        first_surname="Perez",
        second_surname="Garcia",
        father_uuid=grandparent_created.uuid
    )
    parent_created = create_person_service(session, parent_data)

    child_data = PersonCreate(
        first_name="Jose",
        first_surname="Perez",
        second_surname="Fernandez",
        father_uuid=parent_created.uuid
    )

    child_created = create_person_service(session, child_data)

    # ACT → updates grandparent father uuid with his grandchild uuid
    update_data = PersonUpdate(
        father_uuid=child_created.uuid
    )

    # ASSERT → error expected
    with pytest.raises(HTTPException) as exc:
        update_person_service(
            session,
            str(grandparent_created.uuid),
            update_data
        )

    assert exc.value.status_code == 400

    # ASSERT check: DB has not changed
    db_grandparent = session.query(Person).filter(
        Person.uuid == str(grandparent_created.uuid)
    ).first()

    db_parent = session.query(Person).filter(
        Person.uuid == str(parent_created.uuid)
    ).first()

    db_child = session.query(Person).filter(
        Person.uuid == str(child_created.uuid)
    ).first()

    assert db_grandparent is not None
    assert db_grandparent.first_name == "Juan"
    assert db_parent.first_name == "Pedro"
    assert db_child.first_name == "Jose"


def test_update_person_cycle_mother_branch(session):

    # ARRANGE

    grandparent_data = PersonCreate(
        first_name="Dolores",
        first_surname="Perez",
        second_surname="Gomez"
    )
    grandparent_created = create_person_service(session, grandparent_data)

    parent_data = PersonCreate(
        first_name="Carmen",
        first_surname="Perez",
        second_surname="Garcia",
        mother_uuid=grandparent_created.uuid
    )
    parent_created = create_person_service(session, parent_data)

    child_data = PersonCreate(
        first_name="Jose",
        first_surname="Perez",
        second_surname="Fernandez",
        mother_uuid=parent_created.uuid
    )

    child_created = create_person_service(session, child_data)

    # ACT → updates grandparent father uuid with his grandchild uuid
    update_data = PersonUpdate(
        mother_uuid=child_created.uuid
    )

    # ASSERT → error expected
    with pytest.raises(HTTPException) as exc:
        update_person_service(
            session,
            str(grandparent_created.uuid),
            update_data
        )

    assert exc.value.status_code == 400

    # ASSERT check: DB has not changed
    db_grandparent = session.query(Person).filter(
        Person.uuid == str(grandparent_created.uuid)
    ).first()

    db_parent = session.query(Person).filter(
        Person.uuid == str(parent_created.uuid)
    ).first()

    db_child = session.query(Person).filter(
        Person.uuid == str(child_created.uuid)
    ).first()

    assert db_grandparent is not None
    assert db_grandparent.first_name == "Dolores"
    assert db_parent.first_name == "Carmen"
    assert db_child.first_name == "Jose"


def test_update_person_multiple_fields(session):

    # ARRANGE
    person = create_person_service(session, PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    ))

    update_data = PersonUpdate(
        biography="Bio",
        nickname="Juani"
    )

    # ACT
    updated = update_person_service(session, str(person.uuid), update_data)

    # ASSERT
    assert updated.biography == "Bio"
    assert updated.nickname == "Juani"

    # DB
    db_person = session.query(Person).filter(
        Person.uuid == str(person.uuid)
    ).first()

    assert db_person.biography == "Bio"
    assert db_person.nickname == "Juani"


def test_update_person_add_parents(session):

    # ARRANGE
    father = create_person_service(session, PersonCreate(
        first_name="Padre",
        first_surname="Perez",
        second_surname="Uno"
    ))

    mother = create_person_service(session, PersonCreate(
        first_name="Madre",
        first_surname="Perez",
        second_surname="Dos"
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Tres"
    ))

    update_data = PersonUpdate(
        father_uuid=father.uuid,
        mother_uuid=mother.uuid
    )

    # ACT
    updated = update_person_service(session, str(child.uuid), update_data)

    # ASSERT
    assert updated.father_uuid == father.uuid
    assert updated.mother_uuid == mother.uuid


def test_update_person_non_existing_person(session):

    fake_uuid = str(uuid.uuid4())

    count_before = session.query(Person).count()

    with pytest.raises(HTTPException) as exc:
        update_person_service(
            session,
            fake_uuid,
            PersonUpdate(biography="Test")
        )

    count_after = session.query(Person).count()

    assert count_before == count_after

    assert exc.value.status_code == 404


def test_update_person_invalid_uuid(session):

    with pytest.raises(HTTPException) as exc:
        update_person_service(
            session,
            "invalid-uuid",
            PersonUpdate(biography="Test")
        )

    assert exc.value.status_code == 400


def test_update_person_parent_and_fields(session):

    father = create_person_service(session, PersonCreate(
        first_name="Padre",
        first_surname="Perez",
        second_surname="Uno"
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Dos"
    ))

    update_data = PersonUpdate(
        father_uuid=father.uuid,
        biography="Nueva bio"
    )

    updated = update_person_service(session, str(child.uuid), update_data)

    assert updated.father_uuid == father.uuid
    assert updated.biography == "Nueva bio"


def test_update_person_empty_payload(session):

    person = create_person_service(session, PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    ))

    updated = update_person_service(
        session,
        str(person.uuid),
        PersonUpdate()
    )

    assert updated.first_name == "Juan"


# GET TESTS

def test_get_persons_success(session):

    create_person_service(session, PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    ))

    create_person_service(session, PersonCreate(
        first_name="Maria",
        first_surname="Lopez",
        second_surname="Diaz"
    ))

    result = get_persons_service(session)

    assert len(result) == 2
    assert result[0].uuid is not None


def test_get_persons_empty(session):

    result = get_persons_service(session)

    assert result == []


def test_get_person_by_id_success(session):

    created = create_person_service(session, PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    ))

    result = get_person_by_id_service(session, str(created.uuid))

    assert result.uuid == created.uuid
    assert result.first_name == "Juan"


def test_get_person_by_id_not_found(session):

    fake_uuid = str(uuid.uuid4())

    with pytest.raises(HTTPException) as exc:
        get_person_by_id_service(session, fake_uuid)

    assert exc.value.status_code == 404


def test_get_person_by_id_invalid_uuid(session):

    with pytest.raises(HTTPException) as exc:
        get_person_by_id_service(session, "invalid-uuid")

    assert exc.value.status_code == 400


def test_get_person_data_integrity(session):

    created = create_person_service(session, PersonCreate(
        first_name="Carlos",
        first_surname="Ruiz",
        second_surname="Martin",
        biography="Test bio"
    ))

    result = get_person_by_id_service(session, str(created.uuid))

    assert result.first_name == "Carlos"
    assert result.biography == "Test bio"


def test_get_person_with_parents(session):

    father = create_person_service(session, PersonCreate(
        first_name="Padre",
        first_surname="Perez",
        second_surname="Uno"
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Dos",
        father_uuid=father.uuid
    ))

    result = get_person_by_id_service(session, str(child.uuid))

    assert result.father_uuid == father.uuid


# DELETE TESTS

def test_delete_person_success(session):

    # ARRANGE
    created = create_person_service(session, PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Gomez"
    ))

    # ACT
    result = delete_person_service(session, str(created.uuid))

    # ASSERT
    assert result["detail"] == "Persona eliminada correctamente"

    # DB check
    db_person = session.query(Person).filter(
        Person.uuid == str(created.uuid)
    ).first()

    assert db_person is None


def test_delete_person_not_found(session):

    fake_uuid = str(uuid.uuid4())

    with pytest.raises(HTTPException) as exc:
        delete_person_service(session, fake_uuid)

    assert exc.value.status_code == 404


def test_delete_person_invalid_uuid(session):

    with pytest.raises(HTTPException) as exc:
        delete_person_service(session, "invalid-uuid")

    assert exc.value.status_code == 400


def test_delete_person_does_not_affect_others(session):

    person1 = create_person_service(session, PersonCreate(
        first_name="Juan",
        first_surname="Perez",
        second_surname="Uno"
    ))

    person2 = create_person_service(session, PersonCreate(
        first_name="Maria",
        first_surname="Perez",
        second_surname="Dos"
    ))

    delete_person_service(session, str(person1.uuid))

    # person2 sigue existiendo
    db_person2 = session.query(Person).filter(
        Person.uuid == str(person2.uuid)
    ).first()

    assert db_person2 is not None
    assert db_person2.first_name == "Maria"


def test_delete_person_with_children_fails(session):

    father = create_person_service(session, PersonCreate(
        first_name="Padre",
        first_surname="Perez",
        second_surname="Uno"
    ))

    create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Dos",
        father_uuid=father.uuid
    ))

    with pytest.raises(HTTPException) as exc:
        delete_person_service(session, str(father.uuid))

    assert exc.value.status_code == 400

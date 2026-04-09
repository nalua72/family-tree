import pytest
import uuid
from fastapi import HTTPException

from app.schemas.persons import PersonCreate
from app.schemas.relationships import RelationshipType
from app.services.relationships_service import (get_ancestors_service,
                                                get_descendants_service,
                                                get_descendants_by_levels_service,
                                                find_relationship_service,
                                                get_relationship_type,
                                                get_movements_from_path
                                                )
from app.services.person_service import create_person_service


def test_get_ancestors_three_levels(session):

    # ARRANGE

    grandparent = create_person_service(session, PersonCreate(
        first_name="Abuelo",
        first_surname="Perez",
        second_surname="Uno"
    ))

    parent = create_person_service(session, PersonCreate(
        first_name="Padre",
        first_surname="Perez",
        second_surname="Dos",
        father_uuid=grandparent.uuid
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Tres",
        father_uuid=parent.uuid
    ))

    valid_set = set((grandparent.uuid, parent.uuid))
    # ACT

    results = get_ancestors_service(session, child.uuid)

    result_set = set(result.uuid for result in results)

    # ASSERT

    assert result_set == valid_set


def test_get_ancestors_two_parents(session):

    # ARRANGE

    father = create_person_service(session, PersonCreate(
        first_name="Padre",
        first_surname="Perez",
        second_surname="Uno"
    ))

    mother = create_person_service(session, PersonCreate(
        first_name="Madre",
        first_surname="Sanchez",
        second_surname="Dos"
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Sanchez",
        father_uuid=father.uuid,
        mother_uuid=mother.uuid
    ))

    valid_set = set((father.uuid, mother.uuid))

    # ACT

    results = get_ancestors_service(session, child.uuid)

    result_set = set(result.uuid for result in results)

    # ASSERT

    assert result_set == valid_set


def test_get_descendents_three_levels(session):

    # ARRANGE

    grandparent = create_person_service(session, PersonCreate(
        first_name="Abuelo",
        first_surname="Perez",
        second_surname="Uno"
    ))

    parent = create_person_service(session, PersonCreate(
        first_name="Padre",
        first_surname="Perez",
        second_surname="Dos",
        father_uuid=grandparent.uuid
    ))

    child = create_person_service(session, PersonCreate(
        first_name="Hijo",
        first_surname="Perez",
        second_surname="Tres",
        father_uuid=parent.uuid
    ))

    valid_set = set((parent.uuid, child.uuid))

    # ACT

    results = get_descendants_service(session, grandparent.uuid)

    result_set = set(result.uuid for result in results)

    # ASSERT

    assert result_set == valid_set


def test_get_descendants_by_levels_success(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid
    ))

    D = create_person_service(session, PersonCreate(
        first_name="D",
        first_surname="D1",
        second_surname="D2",
        father_uuid=B.uuid
    ))

    E = create_person_service(session, PersonCreate(
        first_name="E",
        first_surname="E1",
        second_surname="E2",
        father_uuid=B.uuid
    ))

    F = create_person_service(session, PersonCreate(
        first_name="F",
        first_surname="F1",
        second_surname="F2",
        father_uuid=C.uuid
    ))

    G = create_person_service(session, PersonCreate(
        first_name="G",
        first_surname="G1",
        second_surname="G2",
        father_uuid=D.uuid
    ))

    H = create_person_service(session, PersonCreate(
        first_name="H",
        first_surname="H1",
        second_surname="H2",
        father_uuid=E.uuid
    ))

    valid_set = [set([B.uuid, C.uuid]), set([
        D.uuid, E.uuid, F.uuid]), set([G.uuid, H.uuid])]

    # ACT

    result_list = get_descendants_by_levels_service(session, A.uuid)

    result_set = [set(p.uuid for p in level) for level in result_list]

    # ASSERT

    assert len(result_set) == len(valid_set)

    for i in range(len(valid_set)):
        assert result_set[i] == valid_set[i]


def test_find_relationship_linear_path_success(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=B.uuid
    ))

    expected_path = [A.uuid, B.uuid, C.uuid]

    # ACT
    result_path = find_relationship_service(session, A.uuid, C.uuid)

    # ASSERT

    assert [r.uuid for r in result_path] == expected_path


def test_find_relationship_reverse_path_success(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=B.uuid
    ))

    expected_path = [C.uuid, B.uuid, A.uuid]

    # ACT
    result_path = find_relationship_service(session, C.uuid, A.uuid)

    # ASSERT

    assert [r.uuid for r in result_path] == expected_path


def test_find_relationship_no_connection_raises_404(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2"
    ))

    # ACT + Assert

    with pytest.raises(HTTPException) as exc:
        find_relationship_service(session, A.uuid, B.uuid)

    assert exc.value.status_code == 404
   # assert "relación" in exc.value.detail.lower()


def test_find_relationship_multiple_paths_returns_shortest(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid
    ))

    E = create_person_service(session, PersonCreate(
        first_name="E",
        first_surname="E1",
        second_surname="E2",
        father_uuid=C.uuid
    ))

    D = create_person_service(session, PersonCreate(
        first_name="D",
        first_surname="D1",
        second_surname="D2",
        father_uuid=B.uuid,
        mother_uuid=E.uuid
    ))

    expected_path = [A.uuid, B.uuid, D.uuid]

    # ACT

    result_path = find_relationship_service(session, A.uuid, D.uuid)

    # ASSERT

    assert [r.uuid for r in result_path] == expected_path


def test_find_relationship_mixed_parent_paths(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        mother_uuid=B.uuid
    ))

    D = create_person_service(session, PersonCreate(
        first_name="D",
        first_surname="D1",
        second_surname="D2",
        father_uuid=C.uuid,
    ))

    expected_path = [A.uuid, B.uuid, C.uuid, D.uuid]

    # ACT
    result_path = find_relationship_service(session, A.uuid, D.uuid)

    # ASSERT

    assert [r.uuid for r in result_path] == expected_path


def test_find_relationship_same_person_returns_single_node(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    expected_path = [A.uuid]

    # ACT

    result_path = find_relationship_service(session, A.uuid, A.uuid)

    # ASSERT

    assert [r.uuid for r in result_path] == expected_path


def test_find_relationship_invalid_uuid_raises_400(session):

    # ARRANGE

    invalid_uuid = "not-a-valid-uuid"

    # ACT + ASSERT

    with pytest.raises(HTTPException) as exc:
        find_relationship_service(session, invalid_uuid, invalid_uuid)

    assert exc.value.status_code == 404
    assert "uuid" in exc.value.detail.lower()


def test_find_relationship_person_not_found_raises_404(session):

    # ARRANGE
    existing = create_person_service(session, PersonCreate(
        first_name="Test",
        first_surname="User",
        second_surname="One"
    ))

    non_existing_uuid = uuid.uuid4()

    # ACT + ASSERT
    with pytest.raises(HTTPException) as exc:
        find_relationship_service(session, existing.uuid, non_existing_uuid)

    assert exc.value.status_code == 404
   # assert "no existe" in exc.value.detail.lower()


def test_get_movements_from_path_child_to_parent_returns_up(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    expected_movement = [1]

    # ACT

    returned_movement = get_movements_from_path(session, [B.uuid, A.uuid])

    # ASSERT

    assert returned_movement == expected_movement


def test_get_movements_from_path_parent_to_child_returns_down(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    expected_movement = [-1]

    # ACT

    returned_movement = get_movements_from_path(session, [A.uuid, B.uuid])

    # ASSERT

    assert returned_movement == expected_movement


def test_get_movements_from_path_multiple_levels_returns_correct_sequence(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=B.uuid
    ))

    # A -> B -> C (parent → child → child)
    expected_movement = [-1, -1]

    # ACT

    returned_movement = get_movements_from_path(
        session, [A.uuid, B.uuid, C.uuid])

    # ASSERT

    assert returned_movement == expected_movement


def test_get_movements_from_path_sibling_path_returns_up_down(session):

    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid
    ))

    # B -> A -> C (child → parent → child)
    expected_movement = [1, -1]

    # ACT

    returned_movement = get_movements_from_path(
        session, [B.uuid, A.uuid, C.uuid])

    # ASSERT

    assert returned_movement == expected_movement


def test_get_movements_from_path_complex_path_returns_correct_sequence(session):
    # ARRANGE

    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid
    ))

    D = create_person_service(session, PersonCreate(
        first_name="D",
        first_surname="D1",
        second_surname="D2",
        father_uuid=B.uuid
    ))

    E = create_person_service(session, PersonCreate(
        first_name="E",
        first_surname="E1",
        second_surname="E2",
        father_uuid=C.uuid
    ))

    # D -> B -> A -> C -> E (child → parent → grandparent → parent → child)
    expected_movement = [1, 1, -1, -1]

    # ACT

    returned_movement = get_movements_from_path(
        session, [D.uuid, B.uuid, A.uuid, C.uuid, E.uuid])

    # ASSERT

    assert returned_movement == expected_movement


def test_get_movements_from_path_non_adjacent_nodes_raises_http_exception(session):

    # ARRANGE
    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=B.uuid
    ))

    # ACT + ASSERT
    with pytest.raises(HTTPException) as exc:
        get_movements_from_path(session, [B.uuid, C.uuid, A.uuid])

    assert exc.value.status_code == 400
    assert "invalid relationship path" in exc.value.detail.lower()


def test_get_relationship_type_same_person_returns_self(session):

    # ARRANGE
    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    expected_relationship = RelationshipType.SELF
    expected_distance = 0

    # ACT

    returned = get_relationship_type(session, A.uuid, A.uuid)

    # ASSERT

    assert returned.relationship == expected_relationship
    assert returned.distance == expected_distance


def test_get_relationship_type_parent_to_child_returns_child(session):

    # ARRANGE
    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    # A is parent of B → relationship should be CHILD
    expected_realtionship = RelationshipType.CHILD
    expected_distance = 1

    # ACT

    returned = get_relationship_type(session, A.uuid, B.uuid)

    # ASSERT

    assert returned.relationship == expected_realtionship
    assert returned.distance == expected_distance


def test_get_relationship_type_child_to_parent_returns_parent(session):

    # ARRANGE
    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    # B is child of A → relationship should be PARENT
    expected_relationship = RelationshipType.PARENT
    expected_distance = 1

    # ACT

    returned = get_relationship_type(session, B.uuid, A.uuid)

    # ASSERT

    assert returned.relationship == expected_relationship
    assert returned.distance == expected_distance


def test_get_relationship_type_siblings_returns_sibling(session):

    # ARRANGE
    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid
    ))

    # B is sibling of C → relationship should be SIBLING
    expected_relationship = RelationshipType.SIBLING
    expected_distance = 2

    # ACT

    returned = get_relationship_type(session, B.uuid, C.uuid)

    # ASSERT

    assert returned.relationship == expected_relationship
    assert returned.distance == expected_distance


def test_get_relationship_type_nephew_returns_nephew(session):

    # ARRANGE
    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid
    ))

    D = create_person_service(session, PersonCreate(
        first_name="D",
        first_surname="D1",
        second_surname="D2",
        father_uuid=B.uuid
    ))

    # D is nephew of C → relationship should be NEPHEW
    expected_relationship = RelationshipType.NEPHEW
    expected_distance = 3

    # ACT

    returned = get_relationship_type(session, C.uuid, D.uuid)

    # ASSERT

    assert returned.relationship == expected_relationship
    assert returned.distance == expected_distance


def test_get_relationship_type_uncle_returns_uncle(session):

    # ARRANGE
    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid
    ))

    D = create_person_service(session, PersonCreate(
        first_name="D",
        first_surname="D1",
        second_surname="D2",
        father_uuid=B.uuid
    ))

    # C is uncle of D → relationship should be UNCLE
    expected_relationship = RelationshipType.UNCLE
    expected_distance = 3

    # ACT

    returned = get_relationship_type(session, D.uuid, C.uuid)

    # ASSERT

    assert returned.relationship == expected_relationship
    assert returned.distance == expected_distance


def test_get_relationship_type_cousins_returns_cousin(session):

    # ARRANGE
    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    B = create_person_service(session, PersonCreate(
        first_name="B",
        first_surname="B1",
        second_surname="B2",
        father_uuid=A.uuid
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid
    ))

    D = create_person_service(session, PersonCreate(
        first_name="D",
        first_surname="D1",
        second_surname="D2",
        father_uuid=B.uuid
    ))

    E = create_person_service(session, PersonCreate(
        first_name="E",
        first_surname="E1",
        second_surname="E2",
        father_uuid=C.uuid
    ))

    # E is cousin of D → relationship should be COUSIN
    expected_relationship = RelationshipType.COUSIN
    expected_distance = 4

    # ACT

    returned = get_relationship_type(session, D.uuid, E.uuid)

    # ASSERT

    assert returned.relationship == expected_relationship
    assert returned.distance == expected_distance

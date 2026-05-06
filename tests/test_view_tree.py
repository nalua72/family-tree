import uuid
from app.schemas.persons import PersonCreate
from app.schemas.tree import PersonNode, PersonTreeViewResponse, FamilyGroup
from app.services.person_service import create_person_service
from app.web.services.tree_view_service import build_tree_view_model


def test_build_tree_view_model_returns_expected_structure(session):

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
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid,
        mother_uuid=B.uuid
    ))

    D = create_person_service(session, PersonCreate(
        first_name="D",
        first_surname="D1",
        second_surname="D2"
    ))

    E = create_person_service(session, PersonCreate(
        first_name="E",
        first_surname="E1",
        second_surname="E2",
        father_uuid=C.uuid,
        mother_uuid=D.uuid
    ))

    A_node = PersonNode(id=str(A.uuid), name=A.first_name,
                        first_surname=A.first_surname, second_surname=A.second_surname)
    B_node = PersonNode(id=str(B.uuid), name=B.first_name,
                        first_surname=B.first_surname, second_surname=B.second_surname)
    C_node = PersonNode(id=str(C.uuid), name=C.first_name,
                        first_surname=C.first_surname, second_surname=C.second_surname)
    D_node = PersonNode(id=str(D.uuid), name=D.first_name,
                        first_surname=D.first_surname, second_surname=D.second_surname)
    E_node = PersonNode(id=str(E.uuid), name=E.first_name,
                        first_surname=E.first_surname, second_surname=E.second_surname)

    expected_result = PersonTreeViewResponse(
        person_to_display=A_node,
        family=[
            FamilyGroup(parents=[A_node, B_node], children=[C_node]),
            FamilyGroup(parents=[C_node, D_node], children=[E_node]),
        ],
    )

    obteined_result = build_tree_view_model(A.uuid, session=session, depth=3)

    assert obteined_result == expected_result


def test_build_tree_view_model_no_child(session):

    # ARRANGE
    A = create_person_service(session, PersonCreate(
        first_name="A",
        first_surname="A1",
        second_surname="A2"
    ))

    A_node = PersonNode(id=str(A.uuid), name=A.first_name,
                        first_surname=A.first_surname, second_surname=A.second_surname)

    expected_result = PersonTreeViewResponse(
        person_to_display=A_node,
        family=[])

    obteined_result = build_tree_view_model(A.uuid, session=session, depth=3)

    assert obteined_result == expected_result


def test_build_tree_view_model_several_children(session):

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
    ))

    C = create_person_service(session, PersonCreate(
        first_name="C",
        first_surname="C1",
        second_surname="C2",
        father_uuid=A.uuid,
        mother_uuid=B.uuid
    ))

    D = create_person_service(session, PersonCreate(
        first_name="D",
        first_surname="D1",
        second_surname="D2",
        father_uuid=A.uuid,
        mother_uuid=B.uuid
    ))

    A_node = PersonNode(id=str(A.uuid), name=A.first_name,
                        first_surname=A.first_surname, second_surname=A.second_surname)
    B_node = PersonNode(id=str(B.uuid), name=B.first_name,
                        first_surname=B.first_surname, second_surname=B.second_surname)
    C_node = PersonNode(id=str(C.uuid), name=C.first_name,
                        first_surname=C.first_surname, second_surname=C.second_surname)
    D_node = PersonNode(id=str(D.uuid), name=D.first_name,
                        first_surname=D.first_surname, second_surname=D.second_surname)

    expected_result = PersonTreeViewResponse(
        person_to_display=A_node,
        family=[
            FamilyGroup(parents=[A_node, B_node], children=[C_node, D_node]),
        ],
    )

    obteined_result = build_tree_view_model(A.uuid, session=session, depth=2)

    assert obteined_result == expected_result

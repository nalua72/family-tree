import pytest
import uuid


def create_person(client, **kwargs):
    res = client.post("/api/persons", json=kwargs)
    assert res.status_code == 201
    return res.json()


# =========================================================
# Happy path
# Validates successful tree responses and depth behavior
# =========================================================


def test_get_tree_single_person_returns_only_root_node(client):

    A = create_person(client,
                      first_name="A",
                      first_surname="A1",
                      second_surname="A2"
                      )
    response = client.get(f"/api/persons/{A['uuid']}/tree")

    assert response.status_code == 200

    data = response.json()
    nodes = data["nodes"]
    edges = data["edges"]

    assert data["root"] == A["uuid"]
    assert len(nodes) == 1
    assert len(edges) == 0


def test_get_tree_default_depth_returns_related_nodes(client):

    # ARRANGE

    # Create A
    A = create_person(client,
                      first_name="A",
                      first_surname="A1",
                      second_surname="A2"
                      )

    # Create B (child of A)
    B = create_person(client,
                      first_name="B",
                      first_surname="B1",
                      second_surname="B2",
                      father_uuid=A["uuid"]
                      )

    # Create C (child of A)
    C = create_person(client,
                      first_name="C",
                      first_surname="C1",
                      second_surname="C2",
                      father_uuid=A["uuid"]
                      )

    response = client.get(f"/api/persons/{A['uuid']}/tree")

    assert response.status_code == 200

    data_returned = response.json()

    assert data_returned["root"] == A["uuid"]
    assert len(data_returned["nodes"]) == 3
    assert len(data_returned["edges"]) == 2


def test_get_tree_depth_query_param_expands_result(client):

    # ARRANGE

    # Create A
    A = create_person(client,
                      first_name="A",
                      first_surname="A1",
                      second_surname="A2"
                      )

    # Create B (child of A)
    B = create_person(client,
                      first_name="B",
                      first_surname="B1",
                      second_surname="B2",
                      father_uuid=A["uuid"]
                      )

    # Create C (child of B)
    C = create_person(client,
                      first_name="C",
                      first_surname="C1",
                      second_surname="C2",
                      father_uuid=B["uuid"]
                      )

    # Create D (child of C)
    D = create_person(client,

                      first_name="D",
                      first_surname="D1",
                      second_surname="D2",
                      father_uuid=C["uuid"]
                      )

    response = client.get(f"/api/persons/{B['uuid']}/tree?depth=2")

    assert response.status_code == 200

    data_returned = response.json()

    assert data_returned["root"] == B["uuid"]

    assert len(data_returned["nodes"]) == 4
    assert len(data_returned["edges"]) == 3

# =========================================================
# HTTP error contract
# Validates request validation and error status codes
# =========================================================


def test_get_tree_invalid_uuid_returns_400(client):

    invalid_uuid = "invalid_uuid"
    response = client.get(f"/api/persons/{invalid_uuid}/tree")

    assert response.status_code == 400


def test_get_tree_unknown_person_returns_404(client):

    unknown_uuid = str(uuid.uuid4())
    response = client.get(f"/api/persons/{unknown_uuid}/tree")

    assert response.status_code == 404


def test_get_tree_negative_depth_returns_422(client):

    A = create_person(client,
                      first_name="A",
                      first_surname="A1",
                      second_surname="A2"
                      )
    response = client.get(f"/api/persons/{A['uuid']}/tree?depth=-2")

    assert response.status_code == 422

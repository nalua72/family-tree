import pytest
import uuid


def test_get_person_success(client):

    A = create_person(client,
                      first_name="A",
                      first_surname="A1",
                      second_surname="A2"
                      )

    response = client.get(f"/api/persons/{A['uuid']}")

    assert response.status_code == 200


def test_get_relationship_type_self(client):

    A = create_person(client,
                      first_name="A",
                      first_surname="A1",
                      second_surname="A2"
                      )

    res = client.get(
        f"/api/relationships/{A['uuid']}/relationship/{A['uuid']}"
    )

    assert res.status_code == 200
    assert res.json()["relationship"] == "SELF"
    assert res.json()["distance"] == 0


def test_find_relationship_path(client):

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

    # Path A → C
    res = client.get(f"/api/relationships/{A['uuid']}/path/{C['uuid']}")

    assert res.status_code == 200

    path = res.json()

    assert len(path) == 3  # A → B → C
    assert path[0]["uuid"] == A["uuid"]
    assert path[-1]["uuid"] == C["uuid"]


def test_get_relationship_type_parent_child(client):

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

    # Path A → B
    res = client.get(
        f"/api/relationships/{A['uuid']}/relationship/{B['uuid']}")

    assert res.status_code == 200

    data = res.json()

    assert data["relationship"] == "CHILD"
    assert data["distance"] == 1


def test_get_relationship_type_siblings(client):

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

    # Path B → C

    res = client.get(
        f"/api/relationships/{B['uuid']}/relationship/{C['uuid']}")

    assert res.status_code == 200
    assert res.json()["relationship"] == "SIBLING"
    assert res.json()["distance"] == 2


def test_get_ancestors(client):

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

    # Path C

    res = client.get(f"/api/relationships/{C['uuid']}/ancestors")

    assert res.status_code == 200

    ancestors = res.json()

    assert len(ancestors) == 2


def test_get_relationship_type_uncle(client):

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

    # Create D (child of B)
    D = create_person(client,
                      first_name="D",
                      first_surname="D1",
                      second_surname="D2",
                      father_uuid=B["uuid"]
                      )
    # Path D → C

    res = client.get(
        f"/api/relationships/{D['uuid']}/relationship/{C['uuid']}")

    assert res.status_code == 200
    assert res.json()["relationship"] == "UNCLE"
    assert res.json()["distance"] == 3


def test_get_relationship_type_nephew(client):

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

    # Create D (child of B)
    D = create_person(client,
                      first_name="D",
                      first_surname="D1",
                      second_surname="D2",
                      father_uuid=B["uuid"]
                      )
    # Path C → D

    res = client.get(
        f"/api/relationships/{C['uuid']}/relationship/{D['uuid']}")

    assert res.status_code == 200
    assert res.json()["relationship"] == "NEPHEW"
    assert res.json()["distance"] == 3


def test_get_relationship_type_cousins(client):

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

    # Create D (child of B)
    D = create_person(client,
                      first_name="D",
                      first_surname="D1",
                      second_surname="D2",
                      father_uuid=B["uuid"]
                      )
    # Create E (child of C)
    E = create_person(client,
                      first_name="E",
                      first_surname="E1",
                      second_surname="E2",
                      father_uuid=C["uuid"]
                      )
    # Path D → E

    res = client.get(
        f"/api/relationships/{D['uuid']}/relationship/{E['uuid']}")

    assert res.status_code == 200
    assert res.json()["relationship"] == "COUSIN"
    assert res.json()["distance"] == 4


def test_relationship_not_found(client):

    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())

    res = client.get(f"/api/relationships/{u1}/relationship/{u2}")

    assert res.status_code == 404


def test_relationship_not_connected_graph(client):

    A = create_person(client,
                      first_name="A", first_surname="A1", second_surname="A2"
                      )

    B = create_person(client,
                      first_name="B", first_surname="B1", second_surname="B2"
                      )

    res = client.get(
        f"/api/relationships/{A['uuid']}/path/{B['uuid']}"
    )

    assert res.status_code == 404


def create_person(client, **kwargs):
    res = client.post("/api/persons", json=kwargs)
    assert res.status_code == 201
    return res.json()

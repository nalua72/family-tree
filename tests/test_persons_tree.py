import pytest


def create_person(client, **kwargs):
    res = client.post("/api/persons", json=kwargs)
    assert res.status_code == 201
    return res.json()


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
    assert nodes[0]["id"] == A["uuid"]
    assert nodes[0]["name"] == "A"
    assert len(edges) == 0


def test_get_tree_depth_1_returns_parents_and_children(client):

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

    returned_nodes = data_returned["nodes"]

    assert len(returned_nodes) == 3

    assert {n["id"] for n in returned_nodes} == {
        A["uuid"], B["uuid"], C["uuid"]}

    returned_edges = data_returned["edges"]

    assert len(returned_edges) == 2

    assert {(e["source"], e["target"]) for e in returned_edges} == {
        (A["uuid"], B["uuid"]), (A["uuid"], C["uuid"])}


def test_get_tree_depth_1_returns_parents_and_children(client):

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

    response = client.get(f"/api/persons/{B['uuid']}/tree")

    assert response.status_code == 200

    data_returned = response.json()

    assert data_returned["root"] == B["uuid"]

    returned_nodes = data_returned["nodes"]

    assert len(returned_nodes) == 3

    assert {n["id"] for n in returned_nodes} == {
        A["uuid"], B["uuid"], C["uuid"]}

    returned_edges = data_returned["edges"]

    assert len(returned_edges) == 2

    assert {(e["source"], e["target"]) for e in returned_edges} == {
        (A["uuid"], B["uuid"]), (B["uuid"], C["uuid"])}


def test_get_tree_depth_2_returns_extended_family(client):

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

    returned_nodes = data_returned["nodes"]

    assert len(returned_nodes) == 4

    assert {n["id"] for n in returned_nodes} == {
        A["uuid"], B["uuid"], C["uuid"], D["uuid"]}

    returned_edges = data_returned["edges"]

    assert len(returned_edges) == 3

    assert {(e["source"], e["target"]) for e in returned_edges} == {
        (A["uuid"], B["uuid"]), (B["uuid"], C["uuid"]), (C["uuid"], D["uuid"])}

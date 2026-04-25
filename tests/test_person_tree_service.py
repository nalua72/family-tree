import uuid
from unittest.mock import patch
import uuid
from app.services.tree_service import get_person_tree_service
from app.schemas.tree import (PersonEdge, PersonNode, PersonTreeResponse)


class FakePerson:
    def __init__(self, uuid, name) -> None:
        self.uuid = uuid
        self.first_name = name
        self.first_surname = "X"
        self.second_surname = "Y"


class FakeGraph:
    def __init__(self, persons: dict[uuid.UUID, FakePerson], relations: dict[uuid.UUID, list[FakePerson]]) -> None:
        self.relations = relations
        self.persons = persons

    def get_neighbors(self, person_uuid) -> list[tuple[str, list[FakePerson]]]:
        parents: list[FakePerson] = []

        children = self.relations.get(person_uuid, [])

        parents = [self.persons[parent_uuid] for parent_uuid, child_list in self.relations.items(
        ) if any(child.uuid == person_uuid for child in child_list)]

        return [("down", children), ("up", parents)]

    def fake_get_neighbors(self, session, person_uuid):
        return self.get_neighbors(person_uuid)


def execute_tree(root: FakePerson, depth: int, persons: dict[uuid.UUID, FakePerson], relations: dict[uuid.UUID, list[FakePerson]]) -> PersonTreeResponse:

    fake_graph = FakeGraph(persons=persons, relations=relations)

    with patch("app.services.tree_service.get_person_by_id_service", return_value=root), patch("app.services.tree_service.get_neighbors", side_effect=fake_graph.fake_get_neighbors):

        return get_person_tree_service(None, root.uuid, depth=depth)


def get_node_ids(person_tree: PersonTreeResponse) -> set[str]:

    return {n.id for n in person_tree.nodes}


def get_edges(person_tree: PersonTreeResponse) -> set[tuple[str, str, str]]:

    return {(e.source, e.target, e.type) for e in person_tree.edges}


# ============================================================
# Basic tree structure
# Validates minimal graph construction and stable relationships
# =============================================================


def test_tree_with_root_only():

    A = FakePerson(uuid.uuid4(), "A")

    # Mock A
    persons = {A.uuid: A}
    relations = {}

    result = execute_tree(A, 0, persons, relations)

    nodes_id = get_node_ids(result)
    edges_set = get_edges(result)

    assert result.root == str(A.uuid)
    assert nodes_id == {str(A.uuid)}
    assert edges_set == set()


def test_tree_with_one_child():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")

    # Mock A -> B
    persons = {A.uuid: A, B.uuid: B}
    relations = {A.uuid: [B]}

    result = execute_tree(A, 1, persons, relations)

    nodes_id = get_node_ids(result)
    edges_set = get_edges(result)

    assert result.root == str(A.uuid)
    assert nodes_id == {str(A.uuid), str(B.uuid)}
    assert edges_set == {(str(A.uuid), str(B.uuid), "parent")}


def test_tree_with_one_parent():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")

    # Mock A -> B
    persons = {A.uuid: A, B.uuid: B}
    relations = {A.uuid: [B]}

    result = execute_tree(B, 1, persons, relations)

    nodes_id = get_node_ids(result)
    edges_set = get_edges(result)

    assert result.root == str(B.uuid)
    assert nodes_id == {str(A.uuid), str(B.uuid)}
    assert edges_set == {(str(A.uuid), str(B.uuid), "parent")}


def test_tree_depth_0_returns_only_root():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")

    # Mock depth = 0
    persons = {A.uuid: A, B.uuid: B}
    relations = {A.uuid: [B]}

    result = execute_tree(A, 0, persons, relations)

    nodes_id = get_node_ids(result)
    edges_set = get_edges(result)

    assert result.root == str(A.uuid)
    assert nodes_id == {str(A.uuid)}
    assert edges_set == set()


def test_tree_depth_1_returns_direct_neighbors_only():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")
    C = FakePerson(uuid.uuid4(), "C")

    # Mock depth = 1
    persons = {A.uuid: A, B.uuid: B, C.uuid: C}
    relations = {A.uuid: [B], B.uuid: [C]}

    result = execute_tree(A, 1, persons, relations)

    nodes_id = get_node_ids(result)
    edges_set = get_edges(result)

    assert result.root == str(A.uuid)
    assert nodes_id == {str(A.uuid), str(B.uuid)}
    assert edges_set == {(str(A.uuid), str(B.uuid), "parent")}


def test_tree_depth_2_returns_second_level_neighbors():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")
    C = FakePerson(uuid.uuid4(), "C")

    # Mock depth = 2
    persons = {A.uuid: A, B.uuid: B, C.uuid: C}
    relations = {A.uuid: [B], B.uuid: [C]}

    result = execute_tree(A, 2, persons, relations)

    nodes_id = get_node_ids(result)
    edges_set = get_edges(result)

    assert result.root == str(A.uuid)
    assert nodes_id == {str(A.uuid), str(B.uuid), str(C.uuid)}
    assert edges_set == {(str(A.uuid), str(B.uuid), "parent"),
                         (str(B.uuid), str(C.uuid), "parent")}

# =========================================================
# Depth traversal
# Validates breadth-first expansion boundaries
# =========================================================


def test_tree_shared_node_is_returned_only_once():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")
    C = FakePerson(uuid.uuid4(), "C")

    # Mock shared node only returned once
    persons = {A.uuid: A, B.uuid: B, C.uuid: C}
    relations = {A.uuid: [C], B.uuid: [C]}

    result = execute_tree(C, 1, persons, relations)

    nodes_id = get_node_ids(result)
    edges_set = get_edges(result)

    assert result.root == str(C.uuid)
    assert nodes_id == {str(A.uuid), str(B.uuid), str(C.uuid)}
    assert edges_set == {(str(A.uuid), str(C.uuid), "parent"),
                         (str(B.uuid), str(C.uuid), "parent")}


def test_tree_repeated_traversal_does_not_duplicate_edges():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")
    C = FakePerson(uuid.uuid4(), "C")

    # Mock nor duplicated  edges
    persons = {A.uuid: A, B.uuid: B, C.uuid: C}
    relations = {A.uuid: [B], B.uuid: [C]}

    result = execute_tree(B, 1, persons, relations)

    nodes_id = get_node_ids(result)
    edges_set = get_edges(result)

    assert result.root == str(B.uuid)
    assert nodes_id == {str(A.uuid), str(B.uuid), str(C.uuid)}
    assert edges_set == {(str(A.uuid), str(B.uuid), "parent"),
                         (str(B.uuid), str(C.uuid), "parent")}


def test_tree_cyclic_graph_does_not_loop_forever():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")

    # Mock not looping
    persons = {A.uuid: A, B.uuid: B}
    relations = {A.uuid: [B], B.uuid: [A]}

    result = execute_tree(A, 1, persons, relations)

    nodes_id = get_node_ids(result)
    edges_set = get_edges(result)

    assert result.root == str(A.uuid)
    assert nodes_id == {str(A.uuid), str(B.uuid)}
    assert edges_set == {(str(A.uuid), str(B.uuid), "parent"),
                         (str(B.uuid), str(A.uuid), "parent")}

# =========================================================
# Output contract
# Validates typed schema consistency in service responses
# =========================================================


def test_tree_returns_person_tree_response():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")

    # Minimal graph: A -> B
    persons = {A.uuid: A, B.uuid: B}
    relations = {A.uuid: [B]}

    result = execute_tree(A, 1, persons, relations)

    assert isinstance(result, PersonTreeResponse)


def test_tree_returns_nodes_as_person_node():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")

    # Minimal graph to validate node typing
    persons = {A.uuid: A, B.uuid: B}
    relations = {A.uuid: [B], B.uuid: [A]}

    result = execute_tree(A, 1, persons, relations)

    assert all(isinstance(node, PersonNode) for node in result.nodes)


def test_tree_returns_edges_as_person_edge():

    A = FakePerson(uuid.uuid4(), "A")
    B = FakePerson(uuid.uuid4(), "B")

    # Minimal graph to validate edge typing
    persons = {A.uuid: A, B.uuid: B}
    relations = {A.uuid: [B], B.uuid: [A]}

    result = execute_tree(A, 1, persons, relations)

    assert all(isinstance(edge, PersonEdge) for edge in result.edges)

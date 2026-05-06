import uuid
from collections import defaultdict
from app.schemas.tree import FamilyGroup, PersonTreeViewResponse
from app.services.tree_service import get_person_tree_service

from sqlalchemy.orm import Session


def build_tree_view_model(root_uuid: uuid.UUID, session: Session, depth: int) -> PersonTreeViewResponse:

    nodes_dict = {}
    family_relations = []
    child_to_parents = defaultdict(list)
    parents_to_children = defaultdict(list)

    relationship_tree = get_person_tree_service(
        session=session, person_uuid=root_uuid, depth=depth)

    # Map the id of a PersonNode to the PersonNode entity
    for person in relationship_tree.nodes:
        nodes_dict[person.id] = person

    # Map the PersonEdge of a person to the parents PersonEdge
    for edge in relationship_tree.edges:
        child_to_parents[edge.target].append(edge.source)

    # Maps the Parents PersonNodes to their common children ParentPerson
    for child, parents in child_to_parents.items():
        key = tuple(sorted(parents))
        parents_to_children[key].append(child)

    # Build the family structure
    for parents, children in parents_to_children.items():

        parents = sorted(parents, key=lambda p: nodes_dict[p].name)
        children = sorted(children, key=lambda c: nodes_dict[c].name)

        family_relations.append(FamilyGroup(
            parents=[nodes_dict[p] for p in parents],
            children=[nodes_dict[c] for c in children]
        ))

    return PersonTreeViewResponse(person_to_display=nodes_dict[str(root_uuid)],
                                  family=family_relations)

import uuid
from collections import defaultdict
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from app.db.sessions import get_db
from sqlalchemy.orm import Session
from typing import Annotated

from app.services.person_service import get_persons_service
from app.services.tree_service import get_person_tree_service
from app.web.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def get_index(request: Request, session: Session = Depends(get_db)):

    person_list = get_persons_service(session=session)

    return templates.TemplateResponse(
        request=request, context={"person_list": person_list}, name="index.html")


@router.get("/nodes/{root_uuid_str}", response_class=HTMLResponse)
def get_index(root_uuid_str: str, request: Request, session: Session = Depends(get_db), depth: Annotated[int, Query(ge=0)] = 1):

    nodes_dict = {}
    family_relations = {"parents": [], "children": []}
    family_relations_list = defaultdict(list)
    inverted_family_relations = defaultdict(list)

    root_uuid = uuid.UUID(root_uuid_str)
    relationship_tree = get_person_tree_service(
        session=session, person_uuid=root_uuid, depth=depth)

    for person in relationship_tree.nodes:
        nodes_dict[person.id] = person

    for edge in relationship_tree.edges:
        family_relations_list[edge.source].append(edge.target)

    # Group parent ID using children as key, converting first the list to a tuple

    for parent_id, children in family_relations_list.items():
        inverted_family_relations[tuple(children)].append(parent_id)

    family_relations = [
        {"parents": [nodes_dict[parent]
                     for parent in parent_list], "children": [nodes_dict[child] for child in list(children_tuple)]} for children_tuple, parent_list in inverted_family_relations.items()]

    # Final formatting
    family_relations_dict = {
        "person_to_display": nodes_dict[root_uuid_str], "family": family_relations}

    return templates.TemplateResponse(
        request=request, context={"person_relationship": family_relations_dict}, name="nodes.html")

import uuid
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.db.sessions import get_db
from sqlalchemy.orm import Session

from app.services.person_service import get_persons_service
from app.services.tree_service import get_person_tree_service
from app.web.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def get_index(request: Request, session: Session = Depends(get_db)):

    person_list = get_persons_service(session=session)

    return templates.TemplateResponse(
        request=request, context={"person_list": person_list}, name="index.html")


@router.get("/nodes", response_class=HTMLResponse)
def get_index(request: Request, session: Session = Depends(get_db)):
    edges_dict: dict[str, list[str]] = {}
    nodes_dict = {}
    relations = []

    # Yo
    # root_uuid = uuid.UUID("93ac9712-da7d-4615-b429-090cbb3b3388")
    # Papa
    # root_uuid = uuid.UUID("efbe542f-070e-4540-b5e6-723d6b947bee")
    # Saul
    root_uuid = uuid.UUID("057274ec-9ef5-4684-b223-2b30640e5109")

    relationship_tree = get_person_tree_service(
        session=session, person_uuid=root_uuid, depth=3)

    for person in relationship_tree.nodes:
        nodes_dict[person.id] = person

    for edge in relationship_tree.edges:
        target_person = nodes_dict[edge.target]

        if edge.source in edges_dict:
            edges_dict[edge.source].append(target_person)
        else:
            edges_dict[edge.source] = [target_person]

    for source, target_list in edges_dict.items():
        for target in target_list:
            relations.append([nodes_dict[source], target, "padre"])

    return templates.TemplateResponse(
        request=request, context={"person_relationship": relations}, name="nodes.html")

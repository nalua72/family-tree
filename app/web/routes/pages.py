from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from app.db.sessions import get_db
from sqlalchemy.orm import Session
from typing import Annotated

from app.services.person_service import get_persons_service, validate_uuid
from app.web.services.tree_view_service import build_tree_view_model

from app.web.templates import templates

router = APIRouter()


@router.get("/", name="home", response_class=HTMLResponse)
def get_index(request: Request, session: Session = Depends(get_db)) -> HTMLResponse:

    person_list = get_persons_service(session=session)

    return templates.TemplateResponse(
        request=request, context={"person_list": person_list}, name="index.html")


@router.get("/nodes/{root_uuid_str}", name="tree_view", response_class=HTMLResponse)
def get_index(root_uuid_str: str,
              request: Request,
              session: Session = Depends(get_db),
              depth: Annotated[int, Query(ge=0)] = 1) -> HTMLResponse:

    root_uuid = validate_uuid(root_uuid_str)

    return templates.TemplateResponse(request=request,
                                      context={"person_relationship": build_tree_view_model(
                                          root_uuid=root_uuid, session=session, depth=depth)},
                                      name="nodes.html")

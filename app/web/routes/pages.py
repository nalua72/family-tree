from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.web.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html")

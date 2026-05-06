from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes.persons import router as persons_router
from app.api.routes.relationships import router as relationships_router

from app.web.routes.pages import router as pages_router


app = FastAPI()

app.include_router(persons_router, prefix="/api")
app.include_router(relationships_router, prefix="/api")


app.include_router(pages_router)


# Moount static directory
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

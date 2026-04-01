from app.api.routes.persons import router as persons_router
from app.api.routes.relationships import router as relationships_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(persons_router, prefix="/api")
app.include_router(relationships_router, prefix="/api")

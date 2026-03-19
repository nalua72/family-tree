import uuid
from app.api.routes.persons import router as persons_router
from fastapi import FastAPI


# from app.schemas.persons import PersonCreate, PersonResponse


app = FastAPI()

app.include_router(persons_router, prefix="/api")

# @app.get("/health")
# def health():
#    return {"status": "OK"}

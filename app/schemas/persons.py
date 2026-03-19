from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PersonBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None


class PersonCreate(PersonBase):
    pass


class PersonResponse(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID

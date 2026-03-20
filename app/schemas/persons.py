from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PersonBase(BaseModel):

    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    first_surname: Optional[str] = Field(None, min_length=1, max_length=50)
    second_surname: Optional[str] = Field(None, min_length=1, max_length=50)

    # Importsant place
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None

    # Birth place
    city_of_birth: Optional[str] = None
    province_of_birth: Optional[str] = None
    country_of_birth: Optional[str] = None

    # Death place
    city_of_death: Optional[str] = None
    province_of_death: Optional[str] = None
    country_of_death: Optional[str] = None

    # Additional personal information
    gender: Optional[str] = None
    marital_status: Optional[str] = None  # single, married, divorced, widow
    biography: Optional[str] = None
    notes: Optional[str] = None
    nickname: Optional[str] = None
    photo_url: Optional[str] = None
    external_reference: Optional[str] = None

    # Parents relationship
    father_uuid: Optional[UUID] = None
    mother_uuid: Optional[UUID] = None

    # Birth order (siblings)
    birth_order: Optional[int] = None


class PersonCreate(PersonBase):
    first_name: str = Field(min_length=1, max_length=50)
    first_surname: str = Field(min_length=1, max_length=50)
    second_surname: str = Field(min_length=1, max_length=50)


class PersonUpdate(PersonBase):
    pass


class PersonResponse(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID

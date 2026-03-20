from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DATE, Text
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///familytree.db", echo=True)

Base = declarative_base()

# Declaring database table "persons"


class Person(Base):
    __tablename__ = "persons"

    uuid = Column(String(36), primary_key=True)
    first_name = Column(String(50), nullable=False)
    first_surname = Column(String(50), nullable=True)
    second_surname = Column(String(50), nullable=True)
    date_of_birth = Column(DATE, nullable=True)
    date_of_death = Column(DATE, nullable=True)
    city_of_birth = Column(String(50), nullable=True)
    province_of_birth = Column(String(50), nullable=True)
    country_of_birth = Column(String(50), nullable=True)
    gender = Column(String(50), nullable=True)
    marital_status = Column(String(50), nullable=True)
    biography = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    nickname = Column(String(50), nullable=True)
    photo_url = Column(String(256), nullable=True)
    external_reference = Column(String(256), nullable=True)
    father_uuid = Column(String(36), nullable=True)
    mother_uuid = Column(String(36), nullable=True)
    birth_order = Column(Integer, nullable=True)


Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

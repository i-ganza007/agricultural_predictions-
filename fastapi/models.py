from typing import List, Optional
from sqlmodel import Relationship, SQLModel, Field
from sqlalchemy import UniqueConstraint
from enum import Enum
import pycountry
from pydantic import validator

# For validation in request body
countries: List[str] = [i.name for i in pycountry.countries] + ["Turkey"]

#For validation in query parameters
class Crops(str, Enum):
    maize = 'Maize'
    potatoes = 'Potatoes'
    sorghum = 'Sorghum'
    soybean = 'Soybeans'
    wheat = 'Wheat'
    rice_paddy = 'Rice, Paddy'  
    cassava = 'Cassava'
    sw_potatoes = 'Sweet Potatoes'  
    plt_others = 'Plantains And Others'  
    yams = 'Yams'
    kijumba = 'Ikijumba'

class Items(SQLModel, table=True):
    item_id: int = Field(primary_key=True)
    item_name: str = Field(max_length=50, nullable=False)

    @validator('item_name')
    def validate_crop(cls, v):
        if v not in [crop.value for crop in Crops]:
            raise ValueError("Invalid {v}")
        return v

class Areas(SQLModel, table=True):
    area_id: int = Field(primary_key=True)
    area_name: str = Field(max_length=50, nullable=False)
    environments: List['Environment'] = Relationship(back_populates='areas')

    @validator('area_name')
    def country_valid(cls, v):
        if v not in countries:
            raise ValueError(f"{v} not in countries list")
        return v

class Environment(SQLModel, table=True):
    # __table_args__ = (UniqueConstraint('area_id', 'year'),)
    year: int = Field(primary_key=True)
    average_rai: float
    pesticides_tavg: float
    temp: float
    area_id: int = Field(foreign_key='areas.area_id', nullable=False, primary_key=True)
    areas: Optional['Areas'] = Relationship(back_populates='environments')

    @validator('year')
    def valid_year(cls, v):
        if not (1980 <= v <= 2025):
            raise ValueError("Not a four digit")
        return v

    @validator('average_rai', 'pesticides_tavg', 'temp')
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError("Not nega")
        return v

class Yield(SQLModel, table=True):
    area_id: int = Field(primary_key=True, foreign_key='areas.area_id')
    item_id: int = Field(primary_key=True, foreign_key='items.item_id')
    year: int = Field(primary_key=True)
    hg_per_ha_yield: float

    @validator('year')
    def valid_year(cls, v):
        if not (1980 <= v <= 2025):
            raise ValueError("Not a four digit")
        return v

    @validator('hg_per_ha_yield')
    def validate_yield(cls, v):
        if v < 0:
            raise ValueError("Not nega")
        return v
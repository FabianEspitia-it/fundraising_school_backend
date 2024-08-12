from pydantic import BaseModel
from typing import List


class Round(BaseModel):
    id: int
    stage: str

    class Config:
        orm_mode = True

class Partner(BaseModel):
    id: int
    name: str
    role: str
    photo: str
    email: str
    twitter: str
    linkedin: str
    crunch_base: str
    website: str
    description: str

    class Config:
        orm_mode = True

class CheckSize(BaseModel):
    id: int
    size: str

    class Config:
        orm_mode = True

class Country(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class Sector(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class FundBase(BaseModel):
    name: str 
    website: str
    description: str
    location: str
    photo: str
    twitter: str
    linkedin: str
    crunch_base: str
    contact: str


class FundCtw(FundBase):
    rounds: List[str] = []
    #partners: List[str] = []
    check_size: List[str] = []
    countries: List[str] = []
    sectors: List[str] = []
    

    class Config:
        orm_mode = True





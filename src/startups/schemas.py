from typing import Union

from pydantic import BaseModel


class NewStartupReq(BaseModel):
    name: str
    email: str
    description: str
    country_code: str
    whatsapp: str
    location: str
    website: str
    linkedin: str
    photo: Union[str, None] = None
    calendly: Union[str, None] = None
    sector: str
    round: str
    checksize: str


class UpdateStartupReq(BaseModel):
    name: Union[str, None] = None
    email: Union[str, None] = None
    description: Union[str, None] = None
    country_code: Union[str, None] = None
    whatsapp: Union[str, None] = None
    location: Union[str, None] = None
    website: Union[str, None] = None
    linkedin: Union[str, None] = None
    photo: Union[str, None] = None
    calendly: Union[str, None] = None
    sector: Union[str, None] = None
    round: Union[str, None] = None
    checksize: Union[str, None] = None

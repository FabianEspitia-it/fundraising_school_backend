from typing import Union

from pydantic import BaseModel


class NewStartupReq(BaseModel):
    name: str
    email: str
    description: str
    phone_number: str
    country: str
    website: str
    linkedin: str
    photo: Union[str, None] = None
    calendly: Union[str, None] = None
    deck: Union[str, None] = None
    sector: str
    round: str
    traction: str

class UpdateStartupReq(BaseModel):
    name: Union[str, None] = None
    email: Union[str, None] = None
    description: Union[str, None] = None
    phone_number: Union[str, None] = None
    country: Union[str, None] = None
    website: Union[str, None] = None
    linkedin: Union[str, None] = None
    photo: Union[str, None] = None
    deck: Union[str, None] = None
    calendly: Union[str, None] = None
    sector: Union[str, None] = None
    round: Union[str, None] = None
    traction: Union[str, None] = None


class CreateBulkStartupReq(BaseModel):
    name: str
    description: str
    phone_number: str
    country: str
    website: str
    photo: Union[str, None] = None
    sector: str
    traction: str
    fund_raised: str

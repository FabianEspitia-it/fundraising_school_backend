from typing import Union

from pydantic import BaseModel
from datetime import datetime


class NewUserReq(BaseModel):
    name: str
    email: str
    linkedin_picture: Union[str, None] = None


class NewUserRes(BaseModel):
    error: str | None = None


class RoundUserReq(BaseModel):
    email: str
    seeking_capital: bool
    accept_terms_and_condition: bool
    round_name: Union[str, None] = None


class ContactUserReq(BaseModel):
    nickname: str
    email: str
    contact_email: str


class ImageUserReq(BaseModel):
    email: str
    image: str


class FavFundReq(BaseModel):
    email: str
    fund_id: int


class FavStartupReq(BaseModel):
    email: str
    startup_id: int

# BD SCHEMAS


class User(BaseModel):
    id: int
    name: str
    followers_amount: int
    phone_number: str
    linkedin_url: str
    location: str
    photo_url: str
    seeking_capital: bool
    round_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime
    is_active: bool = True

    class Config:
        orm_mode = True


class Round(BaseModel):
    id: int
    stage: str

    class Config:
        orm_mode = True


class Job(BaseModel):
    id: int
    name: str
    website_url: str
    url_logo: str
    amount_employees: int
    country: str
    industry: str
    linkedin_url: str
    current: bool
    rol: str
    start_year: datetime
    end_year: datetime

    class Config:
        orm_mode = True


class Education(BaseModel):
    id: int
    degree_name: str
    school_name: str
    url_school_logo: str
    linkedin_url: str
    start_year: datetime
    end_year: datetime
    user_id: int

    class Config:
        orm_mode = True


class UpdateUserReq(BaseModel):

    nickname: Union[str, None] = None
    contact_email: Union[str, None] = None
    phone_number: Union[str, None] = None
    photo_url: Union[str, None] = None
    seeking_capital: Union[bool, None] = None
    location: Union[str, None] = None
    round: Union[str, None] = None


class UserStartupReq(BaseModel):
    nickname: str
    email: str
    linkedin_url: str
    phone_number: str
    location: str
    startup_name: str
    startup_url: str
    role: str
    main_industry: str


    class Config:
        orm_mode = True


class UserNormal(BaseModel):
    nickname: str
    email: str
    country_code: str
    phone_number: str
    location: str

    class Config:
        orm_mode = True


class UserAttendee(BaseModel):
    email: str
    startup_name: str
    job_level: str
    ecosystem_role: str

    class Config:
        orm_mode = True


class UserInvestor(BaseModel):
    email: str
    investment_stage: str
    investment_geography: str
    industry_to_invest: str
    check_size: str

    class Config:
        orm_mode = True


class UserStartup(BaseModel):
    email: str
    startup_name: str
    startup_url: str
    role: str
    main_industry: str

    class Config:
        orm_mode = True


class UserFundCtw(BaseModel):
    nickname: str
    email: str
    photo: str
    role: str
    linkedin_url: str
    fund_name: str

    class Config:
        orm_mode = True






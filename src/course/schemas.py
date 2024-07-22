from pydantic import BaseModel

from typing import Union
from datetime import datetime

class NewClass(BaseModel):
    title: str
    video_link: str
    description: str
    previous_id: Union[int, None] = None
    next_id: Union[int, None] = None
    module_id: int


class NewEvent(BaseModel):
    title: str
    description: str
    date: datetime


class NewCourse(BaseModel):
    title: str
    description: str
    
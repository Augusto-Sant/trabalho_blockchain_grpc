from pydantic import BaseModel
from typing import List


class InsuranceIn(BaseModel):
    id: str
    value: float


class InsuranceOut(BaseModel):
    id: str
    value: float
    created_at: str


class UserCreate(BaseModel):
    name: str
    email: str


class UserRead(UserCreate):
    id: int

    class Config:
        from_attributes = True

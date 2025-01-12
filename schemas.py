from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class AudioCreate(BaseModel):
    name: str
    category: Optional[str]

class CategoryBase(BaseModel):
    name: str
    label: Optional[str]
    color: Optional[str]
    description: Optional[str]

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    audio_count: int
    pass

    class Config:
        from_attributes = True
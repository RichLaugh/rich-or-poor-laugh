from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Audio(Base):
    __tablename__ = "audio"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, index=False, nullable=False)
    user_id = Column(Integer, unique=False, index=False, nullable=False)
    category = Column(String, unique=False, index=False, nullable=False)
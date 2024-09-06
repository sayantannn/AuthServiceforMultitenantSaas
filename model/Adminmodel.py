import pytz
from sqlalchemy import BigInteger, Column, JSON, Date
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict
import datetime
import time

def current_timestamp() -> int:
    utc_now = datetime.datetime.utcnow()
    ist_tz = pytz.timezone('Asia/Kolkata')
    ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ist_tz)
    return int(ist_now.timestamp())

class Organization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    status: int = Field(default=0)
    personal: Optional[bool] = None
    settings: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    created_at: Optional[int] = Field(default_factory=current_timestamp, sa_column=Column(BigInteger))  # Store as BIGINT
    updated_at: Optional[int] = Field(default_factory=current_timestamp, sa_column=Column(BigInteger))  # Store as BIGINT

    roles: List["Role"] = Relationship(back_populates="organization")
    members: List["Member"] = Relationship(back_populates="organization")

    class Config:
        arbitrary_types_allowed = True


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password: str
    profile: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: int = Field(default=0)
    settings: Optional[Dict] = Field(default_factory=dict, sa_column=Column(JSON))
    
    created_at: Optional[int] = Field(default_factory=current_timestamp, sa_column=Column(BigInteger))  # Store as BIGINT
    updated_at: Optional[int] = Field(default_factory=current_timestamp, sa_column=Column(BigInteger))  # Store as BIGINT

    members: List["Member"] = Relationship(back_populates="user")


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    org_id: int = Field(foreign_key="organization.id")
    
    organization: Organization = Relationship(back_populates="roles")
    members: List["Member"] = Relationship(back_populates="role")


class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: int = Field(foreign_key="organization.id")
    user_id: int = Field(foreign_key="user.id")
    role_id: int = Field(foreign_key="role.id")
    status: int = Field(default=0)
    settings: Optional[Dict] = Field(default_factory=dict, sa_column=Column(JSON))
    
    created_at: Optional[int] = Field(default_factory=current_timestamp, sa_column=Column(BigInteger))  # Store as BIGINT
    updated_at: Optional[int] = Field(default_factory=current_timestamp, sa_column=Column(BigInteger))  # Store as BIGINT

    organization: Organization = Relationship(back_populates="members")
    user: User = Relationship(back_populates="members")
    role: Role = Relationship(back_populates="members")
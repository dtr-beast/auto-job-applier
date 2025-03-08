from sqlmodel import Field, SQLModel, Session, create_engine


from typing import Optional
from datetime import datetime
from pydantic import Json


class ApolloContact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(default=None, unique=True, index=True)
    name: Optional[str] = None
    title: Optional[str] = None
    organization_name: Optional[str] = None
    linkedin_url: Optional[str] = None
    company_linkedin_url: Optional[str] = None
    created_at: Optional[datetime] = None
    json_data: Optional[Json] = None
    first_name: Optional[str] = None
    is_valid: Optional[bool] = None

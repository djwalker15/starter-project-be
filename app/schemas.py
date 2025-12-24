# app/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------
# Common base config
# ---------------------------------------------------------


class ORMModel(BaseModel):
    """Base for read models coming from SQLAlchemy."""

    model_config = ConfigDict(from_attributes=True)  # <- Pydantic v2: replaces orm_mode=True


# ---------------------------------------------------------
# Greeting
# ---------------------------------------------------------


class GreetingBase(BaseModel):
    sender: str = Field(..., min_length=1, max_length=50)
    recipient: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=280)


class GreetingCreate(GreetingBase):
    pass


class GreetingUpdate(BaseModel):
    sender: str | None = Field(None, min_length=1, max_length=50)
    recipient: str | None = Field(None, min_length=1, max_length=50)
    message: str | None = Field(None, min_length=1, max_length=280)


class GreetingRead(ORMModel):
    id: UUID
    sender: str
    recipient: str
    message: str
    created_at: datetime


# ---------------------------------------------------------
# Convenience response wrappers (optional)
# ---------------------------------------------------------


class DeleteResult(BaseModel):
    success: bool = True


T = TypeVar("T", bound=BaseModel)


class Page(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)
    total: int
    limit: int
    offset: int
    items: list[T]


# app/schemas.py (bottom of file)
try:
    # Resolve forward refs for all exported models that use postponed annotations / generics
    GreetingRead.model_rebuild()
    Page.model_rebuild()
except Exception:
    # Safe to ignore at import time if some models aren't in scope yet
    pass

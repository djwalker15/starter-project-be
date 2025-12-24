from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session # Typed as Session but actual object is AsyncSession in modern fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Greeting
from app.schemas import GreetingCreate, GreetingRead, GreetingUpdate

# Alias for the dependency
DbSession = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter(prefix="/greetings", tags=["greetings"])


@router.get("/", response_model=list[GreetingRead])
async def list_greetings(db: DbSession) -> list[Greeting]:
    result = await db.execute(select(Greeting))
    return list(result.scalars().all())


@router.post("/", response_model=GreetingRead, status_code=status.HTTP_201_CREATED)
async def create_greeting(payload: GreetingCreate, db: DbSession) -> Greeting:
    obj = Greeting(**payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/{greeting_id}", response_model=GreetingRead)
async def get_greeting(greeting_id: str, db: DbSession) -> Greeting:
    obj = await db.get(Greeting, greeting_id)
    if not obj:
        raise HTTPException(404, "Greeting not found")
    return obj


@router.patch("/{greeting_id}", response_model=GreetingRead)
async def update_greeting(greeting_id: str, payload: GreetingUpdate, db: DbSession) -> Greeting:
    obj = await db.get(Greeting, greeting_id)
    if not obj:
        raise HTTPException(404, "Greeting not found")
    
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
        
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{greeting_id}", response_model=dict)
async def delete_greeting(greeting_id: str, db: DbSession) -> dict[str, bool]:
    obj = await db.get(Greeting, greeting_id)
    if not obj:
        raise HTTPException(404, "Greeting not found")
    await db.delete(obj)
    await db.commit()
    return {"success": True}
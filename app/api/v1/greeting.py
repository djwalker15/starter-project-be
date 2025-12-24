from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Greeting
from app.schemas import GreetingCreate, GreetingRead, GreetingUpdate

DbSession = Annotated[Session, Depends(get_db)]  # optional alias

router = APIRouter(prefix="/greetings", tags=["greetings"])


@router.get("/", response_model=list[GreetingRead])
def list_greetings(db: DbSession) -> list[Greeting]:
    return db.query(Greeting).all()


@router.post("/", response_model=GreetingRead, status_code=status.HTTP_201_CREATED)
def create_greeting(payload: GreetingCreate, db: DbSession) -> Greeting:
    obj = Greeting(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{greeting_id}", response_model=GreetingRead)
def get_greeting(greeting_id: str, db: DbSession) -> Greeting:
    obj = db.get(Greeting, greeting_id)
    if not obj:
        raise HTTPException(404, "Greeting not found")
    return obj
    pass


@router.patch("/{greeting_id}", response_model=GreetingRead)
def update_greeting(greeting_id: str, payload: GreetingUpdate, db: DbSession) -> Greeting:
    obj = db.get(Greeting, greeting_id)
    if not obj:
        raise HTTPException(404, "Greeting not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{greeting_id}", response_model=dict)
def delete_greeting(greeting_id: str, db: DbSession) -> dict[str, bool]:
    obj = db.get(Greeting, greeting_id)
    if not obj:
        raise HTTPException(404, "Greeting not found")
    db.delete(obj)
    db.commit()
    return {"success": True}

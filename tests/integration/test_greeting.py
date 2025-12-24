from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from app.models import Greeting

endpoint = "/api/v1/greetings/"


def add_greeting(
    db: Session, *, sender: str = "John Doe", recipient: str = "World", message: str = "Hello"
) -> Greeting:
    """Create and persist a Greeting row; return the ORM object with ID."""
    obj = Greeting(sender=sender, recipient=recipient, message=message)
    db.add(obj)
    db.flush()  # assigns PK (uuid) without committing
    return obj


@pytest.mark.anyio
async def test_list_greeting(async_client, db_session: Session):
    # Arrange: seed two rows (directly in this test)
    add_greeting(db_session, sender="Alice", recipient="Bob", message="Hi")
    add_greeting(db_session, sender="John", recipient="Jane", message="Yo")

    # Act
    resp = await async_client.get(endpoint)
    assert resp.status_code == 200
    data = resp.json()

    # Assert
    assert isinstance(data, list)

    assert len(data) == 2
    assert "id" in data[0] and "created_at" in data[0]
    assert "id" in data[1] and "created_at" in data[1]
    assert data[0]["sender"] == "Alice"
    assert data[0]["recipient"] == "Bob"
    assert data[0]["message"] == "Hi"
    assert data[1]["sender"] == "John"
    assert data[1]["recipient"] == "Jane"
    assert data[1]["message"] == "Yo"


@pytest.mark.anyio
async def test_create_greeting(async_client, db_session: Session):
    # Act
    payload = {"sender": "John", "recipient": "Jane", "message": "Hello"}
    resp = await async_client.post(endpoint, json=payload)
    assert resp.status_code == 201
    created = resp.json()

    # Assert response shape against your GreetingRead schema
    assert "id" in created and "created_at" in created
    assert created["sender"] == "John"
    assert created["recipient"] == "Jane"
    assert created["message"] == "Hello"

    # Assert DB side
    obj = db_session.get(Greeting, uuid.UUID(created["id"]))
    assert obj is not None
    assert obj.sender == "John"
    assert obj.recipient == "Jane"
    assert obj.message == "Hello"


@pytest.mark.anyio
async def test_get_greeting(async_client, db_session: Session):
    # Arrange
    row = add_greeting(db_session, sender="Carlos", recipient="Diana", message="Hola")

    # Act
    resp = await async_client.get(f"{endpoint}{row.id}")
    assert resp.status_code == 200
    data = resp.json()

    # Assert
    assert data["id"] == str(row.id)
    assert data["sender"] == "Carlos"
    assert data["recipient"] == "Diana"
    assert data["message"] == "Hola"
    assert "created_at" in data


@pytest.mark.anyio
async def test_update_greeting(async_client, db_session: Session):
    # Arrange
    row = add_greeting(db_session, sender="Erin", recipient="Fred", message="Bonjour")

    # Act (PATCH supports partials)
    patch = {"message": "Howdy"}
    resp = await async_client.patch(f"{endpoint}{row.id}", json=patch)
    assert resp.status_code == 200
    updated = resp.json()

    # Assert response
    assert updated["id"] == str(row.id)
    assert updated["sender"] == "Erin"
    assert updated["recipient"] == "Fred"
    assert updated["message"] == "Howdy"
    assert "created_at" in updated

    # Assert DB
    db_session.refresh(row)
    assert row.message == "Howdy"


@pytest.mark.anyio
async def test_delete_greeting(async_client, db_session: Session):
    # Arrange
    row = add_greeting(db_session, sender="Gabby", recipient="Harold", message="Yo")

    # Act
    resp = await async_client.delete(f"{endpoint}{row.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"success": True} or body.get("success") is True

    # Assert DB
    gone = db_session.get(Greeting, row.id)
    assert gone is None

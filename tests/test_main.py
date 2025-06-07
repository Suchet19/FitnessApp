import time
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models import FitnessClass as Class, Booking, Base

@pytest.fixture(scope="function")
def db_session():
    from sqlalchemy.orm import Session
    from app.database import engine

    # Clear all tables before each test.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_list_classes(client, db_session):
    # Seed a sample class (only one will exist after dropping dummy data).
    test_class = Class(
        name="Yoga Basics",
        instructor="John Doe",
        start_time_epoch=int((datetime.utcnow() + timedelta(days=1)).timestamp()),
        available_slots=10,
    )
    db_session.add(test_class)
    db_session.commit()

    response = client.get("/classes?tz=America/New_York")
    assert response.status_code == 200
    data = response.json()
    # Expect exactly one class now.
    assert len(data) == 1
    assert data[0]["name"] == "Yoga Basics"
    # Check time conversion returns an int.
    assert isinstance(data[0]["start_time_epoch"], int)

def test_book_class(client, db_session):
    test_class = Class(
        name="HIIT Workout",
        instructor="Jane Smith",
        start_time_epoch=int((datetime.utcnow() + timedelta(days=1)).timestamp()),
        available_slots=5,
    )
    db_session.add(test_class)
    db_session.commit()
    db_session.refresh(test_class)

    booking_data = {
        "class_id": test_class.id,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    response = client.post("/book", json=booking_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Booking confirmed"

    db_session.refresh(test_class)
    assert test_class.available_slots == 4

def test_book_class_full(client, db_session):
    # Create a class with only one available slot.
    test_class = Class(
        name="Zumba Fun",
        instructor="Zara",
        start_time_epoch=int((datetime.utcnow() + timedelta(days=1)).timestamp()),
        available_slots=1,
    )
    db_session.add(test_class)
    db_session.commit()
    db_session.refresh(test_class)

    # First booking should succeed.
    booking_data = {
        "class_id": test_class.id,
        "client_name": "First Booker",
        "client_email": "first@example.com"
    }
    response = client.post("/book", json=booking_data)
    assert response.status_code == 200
    db_session.refresh(test_class)
    assert test_class.available_slots == 0

    # Second booking should fail with a 400 error.
    second_booking = {
        "class_id": test_class.id,
        "client_name": "Second Booker",
        "client_email": "second@example.com"
    }
    response = client.post("/book", json=second_booking)
    assert response.status_code == 400
    data = response.json()
    # Expect an error message (for example, "No slots left").
    assert "No slots left" in data["detail"]

def test_list_bookings(client, db_session):
    # Create a class and add a booking.
    test_class = Class(
        name="Pilates",
        instructor="Alice Brown",
        start_time_epoch=int((datetime.utcnow() + timedelta(days=1)).timestamp()),
        available_slots=8,
    )
    db_session.add(test_class)
    db_session.commit()
    db_session.refresh(test_class)

    test_booking = Booking(
        class_id=test_class.id,
        client_name="Test User",
        client_email="test@example.com",
        booked_at=int(time.time())
    )
    db_session.add(test_booking)
    db_session.commit()

    response = client.get("/bookings?email=test@example.com&tz=America/New_York")
    assert response.status_code == 200
    data = response.json()
    # Expect a single booking.
    assert len(data) == 1
    assert data[0]["client_name"] == "Test User"
    # Validate that class_name was populated from the join query.
    assert isinstance(data[0]["class_name"], str)

def test_invalid_timezone(client, db_session):
    # Seed a sample class.
    test_class = Class(
        name="Spin Class",
        instructor="Sam",
        start_time_epoch=int((datetime.utcnow() + timedelta(days=1)).timestamp()),
        available_slots=15,
    )
    db_session.add(test_class)
    db_session.commit()

    # Using an invalid timezone should yield a 400 error.
    response = client.get("/bookings?email=test@example.com&tz=Invalid/Timezone")
    assert response.status_code == 400
    data = response.json()
    assert "Invalid timezone" in data["detail"]
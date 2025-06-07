from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, FitnessClass, Booking
from app.schemas import BookingRequest, FitnessClassResponse, BookingResponse
import time
from datetime import datetime
import pytz
from typing import List
import os

app = FastAPI()

# Create DB tables
Base.metadata.create_all(bind=engine)

def add_dummy_classes():

    if os.getenv("TESTING"):
        return
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(FitnessClass).delete()
        db.commit()

        now = int(time.time())
        classes = [
            FitnessClass(
                name="Yoga Basics",
                instructor="Alice",
                start_time_epoch=now + 3600,
                available_slots=10,
            ),
            FitnessClass(
                name="HIIT Blast",
                instructor="Bob",
                start_time_epoch=now + 7200,
                available_slots=8,
            ),
            FitnessClass(
                name="Pilates Core",
                instructor="Carol",
                start_time_epoch=now + 10800,
                available_slots=12,
            ),
        ]
        db.add_all(classes)
        db.commit()
    finally:
        db.close()

add_dummy_classes()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/classes", response_model=list[FitnessClassResponse])
def get_classes(db: Session = Depends(get_db)):
    return db.query(FitnessClass).all()

@app.post("/book")
def book_class(payload: BookingRequest, db: Session = Depends(get_db)):
    cls = db.query(FitnessClass).filter(FitnessClass.id == payload.class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    if cls.available_slots <= 0:
        raise HTTPException(status_code=400, detail="No slots left")

    cls.available_slots -= 1
    booking = Booking(
        class_id=cls.id,
        client_name=payload.client_name,
        client_email=payload.client_email,
        booked_at=int(time.time())
    )
    db.add(booking)
    db.commit()
    return {"message": "Booking confirmed"}

@app.get("/bookings", response_model=List[BookingResponse])
def get_bookings(
    email: str = Query(..., description="Email address to search bookings for"),
    tz: str = Query("UTC", description="Timezone for displaying times"),
    db: Session = Depends(get_db)
):
    try:
        # Validate timezone
        timezone = pytz.timezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {tz}")


    bookings = (
        db.query(Booking, FitnessClass.name)
        .join(FitnessClass, Booking.class_id == FitnessClass.id)
        .filter(Booking.client_email == email)
        .order_by(Booking.booked_at.desc())
        .all()
    )


    response_bookings = []
    for booking, class_name in bookings:
        response_bookings.append(
            BookingResponse(
                id=booking.id,
                class_id=booking.class_id,
                client_name=booking.client_name,
                client_email=booking.client_email,
                booked_at=booking.booked_at,
                class_name=class_name
            )
        )

    return response_bookings
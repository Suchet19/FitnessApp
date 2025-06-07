from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional
import logging

from . import models, schemas

logger = logging.getLogger(__name__)

def get_all_classes(db: Session) -> List[models.Class]:
    """Fetch upcoming classes (whose start_time is in the future)."""
    current_time = int(datetime.utcnow().timestamp())
    classes = db.query(models.Class).filter(models.Class.start_time > current_time).order_by(models.Class.start_time).all()
    logger.info(f"Fetched {len(classes)} upcoming classes.")
    return classes

def get_class_by_id(db: Session, class_id: int) -> Optional[models.Class]:
    """Retrieve a class by its ID."""
    return db.query(models.Class).filter(models.Class.id == class_id).first()

def create_booking(db: Session, booking: schemas.BookingCreate) -> models.Booking:
    """Create a booking while decrementing the available slots.
       Uses row-level locking to prevent race conditions."""
    try:

        class_obj = db.query(models.Class).with_for_update().filter(models.Class.id == booking.class_id).first()
        if not class_obj:
            raise ValueError("Class not found")
        if class_obj.available_slots <= 0:
            raise ValueError("Class is full")

        db_booking = models.Booking(**booking.model_dump())
        class_obj.available_slots -= 1
        db.add(db_booking)
        db.flush()  # Generate booking ID.
        db_booking.class_obj = class_obj
        db.commit()
        logger.info(f"Created booking {db_booking.id} for class {class_obj.id}")
        return db_booking
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking: {str(e)}")
        raise

def get_client_bookings(db: Session, email: str) -> List[models.Booking]:
    """Get all bookings for a client indicated by email."""
    bookings = db.query(models.Booking).options(joinedload(models.Booking.class_obj))\
                 .filter(models.Booking.client_email == email)\
                 .order_by(models.Booking.created_at.desc()).all()
    logger.info(f"Found {len(bookings)} bookings for client {email}")
    return bookings

def suggest_alternative_classes(db: Session, current_class: models.Class) -> List[models.Class]:
    """Suggest up to 3 alternative upcoming classes with available slots."""
    current_time = int(datetime.utcnow().timestamp())
    alternatives = db.query(models.Class).filter(
        and_(
            models.Class.start_time >= current_time,
            models.Class.available_slots > 0,
            models.Class.id != current_class.id
        )
    ).order_by(models.Class.start_time).limit(3).all()
    return alternatives

def create_class(db: Session, class_data: schemas.ClassCreate) -> models.Class:
    """Create a new fitness class."""
    db_class = models.Class(**class_data.model_dump())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    logger.info(f"Created new class {db_class.id}")
    return db_class
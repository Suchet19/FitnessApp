from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FitnessClass(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    instructor = Column(String)
    start_time_epoch = Column(Integer)  # store as UTC timestamp
    available_slots = Column(Integer)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer)
    client_name = Column(String)
    client_email = Column(String)
    booked_at = Column(Integer)  # UTC timestamp
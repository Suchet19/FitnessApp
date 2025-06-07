from pydantic import BaseModel, EmailStr

class BookingRequest(BaseModel):
    class_id: int
    client_name: str
    client_email: EmailStr

class FitnessClassResponse(BaseModel):
    id: int
    name: str
    instructor: str
    start_time_epoch: int
    available_slots: int

class BookingResponse(BaseModel):
    id: int
    class_id: int
    client_name: str
    client_email: str
    booked_at: int
    class_name: str | None = None  # Will be populated from the joined query
# Fitness Studio Class Booking System

A FastAPI-based booking system for fitness classes with features like class listing, booking management, and timezone support.

## Features

- List upcoming fitness classes
- Book classes with automatic slot management
- View client bookings
- Timezone support for class times
- Race condition handling for bookings
- Alternative class suggestions when a class is full

## Tech Stack

- FastAPI
- SQLAlchemy ORM
- SQLite database
- Pydantic for data validation
- Pytest for testing

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

4. Run tests:
```bash
pytest
```

## Docker Setup

1. Build the Docker image:
```bash
docker build -t fitness-booking .
```

2. Run the container:
```bash
docker run -p 8000:8000 fitness-booking
```

## API Endpoints

### List Classes
```bash
GET /classes?tz=America/New_York
```

### Book a Class
```bash
POST /book
{
    "class_id": 1,
    "client_name": "John Doe",
    "client_email": "john@example.com"
}
```

### List Client Bookings
```bash
GET /bookings?email=john@example.com&tz=America/New_York
```

## Example cURL Commands

### List Classes
```bash
curl -X GET "http://localhost:8000/classes?tz=America/New_York"
```

### Book a Class
```bash
curl -X POST "http://localhost:8000/book" \
     -H "Content-Type: application/json" \
     -d '{
         "class_id": 1,
         "client_name": "John Doe",
         "client_email": "john@example.com"
     }'
```

### List Bookings
```bash
curl -X GET "http://localhost:8000/bookings?email=john@example.com&tz=America/New_York"
```

## Error Handling

The API returns appropriate HTTP status codes and structured error responses:

- 200: Success
- 400: Bad Request (e.g., class full)
- 404: Not Found
- 500: Internal Server Error

## Timezone Support

All times are stored internally as UTC timestamps. The API accepts a `tz` query parameter to convert times to the user's local timezone. Example timezones:

- America/New_York
- Europe/London
- Asia/Tokyo
- Australia/Sydney 

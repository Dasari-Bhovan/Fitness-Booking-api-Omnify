
# 🏃‍♀️ Fitness Booking API

A comprehensive RESTful API for managing fitness class bookings with timezone support, built with FastAPI, SQLAlchemy, and SQLite.

## ✨ Features

- **Complete CRUD Operations**: Manage fitness classes and bookings
- **Timezone Management**: Automatic timezone conversion with IST as base
- **Robust Validation**: Comprehensive input validation using Pydantic
- **Error Handling**: Detailed error responses with proper HTTP status codes
- **Modular Architecture**: Clean separation of concerns with service layer
- **Comprehensive Testing**: Full test suite with pytest
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Logging**: Structured logging throughout the application

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**

   ```bash

   git clone <repository-url>

   cd fitness-booking-api

   ```
2. **Create virtual environment**

   ```bash

   python -m venv venv

   source venv/bin/activate  # On Windows: venv\Scripts\activate

   ```
3. **Install dependencies**

   ```bash

   pip install -r requirements.txt

   ```
4. **Run the application**

   ```bash

   python -m app.main

   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints

### 1. Get All Classes

```http

GET /api/v1/classes?timezone=Asia/Kolkata

```

**Response:**

```json
[
  {
    "id": 1,

    "name": "Morning Yoga",

    "description": "Start your day with peaceful yoga practice",

    "instructor": "Sarah Johnson",

    "class_datetime": "2024-01-15T08:00:00+05:30",

    "duration_minutes": 60,

    "max_slots": 15,

    "available_slots": 12,

    "booked_slots": 3,

    "is_fully_booked": false,

    "is_active": true,

    "created_at": "2024-01-10T10:00:00+05:30"
  }
]
```

### 2. Create Booking

```http

POST /api/v1/book

Content-Type: application/json


{

  "class_id": 1,

  "client_name": "John Doe",

  "client_email": "john.doe@example.com",

  "notes": "First time booking"

}

```

**Response:**

```json
{
  "id": 1,

  "class_id": 1,

  "client_name": "John Doe",

  "client_email": "john.doe@example.com",

  "notes": "First time booking",

  "booking_reference": "FB12345678",

  "booking_status": "confirmed",

  "created_at": "2024-01-10T10:30:00+05:30",

  "fitness_class": {
    "id": 1,

    "name": "Morning Yoga",

    "instructor": "Sarah Johnson"

    // ... other class details
  }
}
```

### 3. Get Bookings by Email

```http

GET /api/v1/bookings?client_email=john.doe@example.com

```

**Response:**

```json
{
  "bookings": [
    {
      "id": 1,

      "class_id": 1,

      "client_name": "John Doe",

      "client_email": "john.doe@example.com",

      "booking_reference": "FB12345678",

      "booking_status": "confirmed",

      "created_at": "2024-01-10T10:30:00+05:30",

      "fitness_class": {
        // ... class details
      }
    }
  ],

  "total_count": 1,

  "client_email": "john.doe@example.com"
}
```

## 🧪 Sample cURL Requests

### Get Classes

```bash

curl -X GET "http://localhost:8000/api/v1/classes" \

  -H "accept: application/json"

```

### Get Classes with Timezone

```bash

curl -X GET "http://localhost:8000/api/v1/classes?timezone=Asia/Kolkata" \

  -H "accept: application/json"

```

### Create Booking

```bash

curl -X POST "http://localhost:8000/api/v1/book" \

  -H "accept: application/json" \

  -H "Content-Type: application/json" \

  -d '{

    "class_id": 1,

    "client_name": "John Doe",

    "client_email": "john.doe@example.com",

    "notes": "Looking forward to the class!"

  }'

```

### Get Bookings

```bash

curl -X GET "http://localhost:8000/api/v1/bookings?client_email=john.doe@example.com" \

  -H "accept: application/json"

```

## 🧪 Testing

Run the test suite:

```bash

# Run all tests

pytest


# Run with coverage

pytest --cov=app


# Run specific test file

pytest tests/test_bookings.py


# Run with verbose output

pytest -v

```

### Project Structure

```

fitness_booking_api/

├── app/

│   ├── main.py              # FastAPI application setup

│   ├── config.py            # Configuration management

│   ├── database/

│   │   └── db_utils.py      # Database setup and session management

│   ├── models/

│   │   └── booking.py       # SQLAlchemy models

│   ├── schemas/

│   │   └── booking.py       # Pydantic schemas

│   ├── services/

│   │   └── booking_service.py # Business logic layer

│   ├── api/

│   │   ├──v1/

│   │       └── routes/

│   │           └── booking.py  # API route handlers

│   └── utils/

│       ├── exceptions.py    # Custom exceptions

│       └── timezone_utils.py # Timezone management

├── tests/

│   └── test_bookings.py     # Comprehensive test suite

├── requirements.txt

├── README.md

```

### Key Design Patterns

1. **Service Layer Pattern**: Business logic separated from API handlers
2. **Repository Pattern**: Data access abstraction through SQLAlchemy
3. **Dependency Injection**: FastAPI's dependency system for database sessions
4. **Schema Validation**: Pydantic models for request/response validation
5. **Exception Handling**: Custom exceptions with proper HTTP status codes

## 🌍 Timezone Support

The API supports timezone conversion for class schedules:

- **Base Timezone**: IST (Asia/Kolkata) as specified in requirements
- **Dynamic Conversion**: Convert class times to any timezone using the `timezone` query parameter
- **Automatic Management**: All datetime operations handle timezone-aware objects

Example:

```bash

# Get classes in New York timezone

curl "http://localhost:8000/api/v1/classes?timezone=Asia/Kolkata"


# Get classes in Tokyo timezone

curl "http://localhost:8000/api/v1/classes?timezone=Asia/Tokyo"

```

## 🔒 Error Handling

The API provides comprehensive error handling with standardized responses:

### Error Response Format

```json
{
  "detail": {
    "message": "Human-readable error message",

    "details": {
      "field": "Additional context"
    },

    "error_type": "error_category"
  }
}
```

### Common Error Scenarios

- **404 Not Found**: Class doesn't exist
- **409 Conflict**: No slots available or duplicate booking
- **422 Validation Error**: Invalid input data
- **500 Internal Server Error**: Unexpected server errors

## 📝 Sample Data

The application automatically creates sample fitness classes on startup:

1. **Morning Yoga** (8:00 AM, 15 slots)
2. **High Energy Zumba** (6:30 PM, 20 slots)
3. **HIIT Intensive** (7:00 PM, 12 slots)

## 🚀 Production Considerations

For production deployment, consider:

1. **Database**: Replace SQLite with PostgreSQL/MySQL
2. **Environment Variables**: Use proper environment configuration
3. **Security**: Add authentication and authorization
4. **Caching**: Implement Redis for session management
5. **Monitoring**: Add application monitoring and logging
6. **Rate Limiting**: Implement API rate limiting
7. **CORS**: Configure CORS for specific origins

## 🤝 Development

### Code Quality

- **Type Hints**: Full type annotation throughout codebase
- **Docstrings**: Comprehensive documentation for all functions
- **Linting**: Code follows PEP 8 standards
- **Testing**: High test coverage with multiple scenarios

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python practices.**

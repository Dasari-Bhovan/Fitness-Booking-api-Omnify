"""
API routes for booking management.
Implements RESTful endpoints with proper error handling and validation.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database.db_utils import get_db
from app.schemas.booking import (
    APIResponse,
    BookingCreate,
    BookingListResponse,
    BookingResponse,
    FitnessClassResponse,
    TimezoneQuery,
)
from app.services.booking import BookingService
from app.utils.exceptions import (
    ClassNotFoundException,
    DuplicateBookingException,
    InvalidBookingDataException,
    NoSlotsAvailableException,
    create_http_exception,
)
from app.utils.timezone_utils import tz_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["bookings"])


@router.get("/classes", response_model=List[FitnessClassResponse])
async def get_classes(
    timezone: Optional[str] = Query(
        "Asia/Kolkata", description="Target timezone (e.g., 'America/New_York')"
    ),
    db: Session = Depends(get_db),
):
    """
    Get all upcoming fitness classes.

    - **timezone**: Optional timezone for datetime conversion
    - Returns list of upcoming active classes with available slots
    """
    try:
        service = BookingService(db)
        classes = service.get_all_classes(timezone=timezone)

        # Convert to response schema
        response_classes = []
        for fitness_class in classes:
            class_dict = {
                "id": fitness_class.id,
                "name": fitness_class.name,
                "description": fitness_class.description,
                "instructor": fitness_class.instructor,
                "class_datetime": fitness_class.class_datetime,
                "duration_minutes": fitness_class.duration_minutes,
                "max_slots": fitness_class.max_slots,
                "available_slots": fitness_class.available_slots,
                "booked_slots": fitness_class.booked_slots,
                "is_fully_booked": fitness_class.is_fully_booked,
                "is_active": fitness_class.is_active,
                "created_at": fitness_class.created_at,
            }
            response_classes.append(FitnessClassResponse(**class_dict))

        return response_classes

    except Exception as e:
        logger.error(f"Error retrieving classes: {e}")
        raise create_http_exception(500, "Failed to retrieve classes")


@router.post("/book", response_model=BookingResponse)
async def create_booking(booking_data: BookingCreate, db: Session = Depends(get_db)):
    """
    Create a new booking for a fitness class.

    - **class_id**: ID of the fitness class to book
    - **client_name**: Full name of the client
    - **client_email**: Email address of the client
    - **notes**: Optional notes for the booking
    """
    try:
        service = BookingService(db)
        booking = service.create_booking(booking_data)

        # Convert to response schema
        booking_dict = {
            "id": booking.id,
            "class_id": booking.class_id,
            "client_name": booking.client_name,
            "client_email": booking.client_email,
            "notes": booking.notes,
            "booking_reference": booking.booking_reference,
            "booking_status": booking.booking_status,
            "created_at": booking.created_at,
            "fitness_class": {
                "id": booking.fitness_class.id,
                "name": booking.fitness_class.name,
                "description": booking.fitness_class.description,
                "instructor": booking.fitness_class.instructor,
                "class_datetime": tz_manager.convert_timezone(
                    booking.fitness_class.class_datetime, settings.DEFAULT_TIMEZONE
                ),
                "duration_minutes": booking.fitness_class.duration_minutes,
                "max_slots": booking.fitness_class.max_slots,
                "available_slots": booking.fitness_class.available_slots,
                "booked_slots": booking.fitness_class.booked_slots,
                "is_fully_booked": booking.fitness_class.is_fully_booked,
                "is_active": booking.fitness_class.is_active,
                "created_at": booking.fitness_class.created_at,
            },
        }

        return BookingResponse(**booking_dict)

    except ClassNotFoundException as e:
        raise create_http_exception(404, e.message, e.details)
    except NoSlotsAvailableException as e:
        raise create_http_exception(409, e.message, e.details)
    except DuplicateBookingException as e:
        raise create_http_exception(409, e.message, e.details)
    except InvalidBookingDataException as e:
        raise create_http_exception(400, e.message, e.details)
    except Exception as e:
        logger.error(f"Unexpected error creating booking: {e}")
        raise create_http_exception(500, "Failed to create booking")


@router.get("/bookings", response_model=BookingListResponse)
async def get_bookings(
    client_email: str = Query(..., description="Client email address"),
    db: Session = Depends(get_db),
):
    """
    Get all bookings for a specific client email.

    - **client_email**: Email address of the client
    - Returns list of all bookings made by the client
    """
    try:
        service = BookingService(db)
        bookings = service.get_bookings_by_email(client_email)

        # Convert to response schema
        response_bookings = []
        for booking in bookings:
            booking_dict = {
                "id": booking.id,
                "class_id": booking.class_id,
                "client_name": booking.client_name,
                "client_email": booking.client_email,
                "notes": booking.notes,
                "booking_reference": booking.booking_reference,
                "booking_status": booking.booking_status,
                "created_at": booking.created_at,
                "fitness_class": {
                    "id": booking.fitness_class.id,
                    "name": booking.fitness_class.name,
                    "description": booking.fitness_class.description,
                    "instructor": booking.fitness_class.instructor,
                    "class_datetime": tz_manager.convert_timezone(
                        booking.fitness_class.class_datetime, settings.DEFAULT_TIMEZONE
                    ),
                    "duration_minutes": booking.fitness_class.duration_minutes,
                    "max_slots": booking.fitness_class.max_slots,
                    "available_slots": booking.fitness_class.available_slots,
                    "booked_slots": booking.fitness_class.booked_slots,
                    "is_fully_booked": booking.fitness_class.is_fully_booked,
                    "is_active": booking.fitness_class.is_active,
                    "created_at": booking.fitness_class.created_at,
                },
            }
            response_bookings.append(BookingResponse(**booking_dict))

        return BookingListResponse(
            bookings=response_bookings,
            total_count=len(response_bookings),
            client_email=client_email,
        )

    except Exception as e:
        logger.error(f"Error retrieving bookings for {client_email}: {e}")
        raise create_http_exception(500, "Failed to retrieve bookings")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Fitness Studio Booking API is running"}

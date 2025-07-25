"""
Custom exception classes for better error handling and API responses.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException


class BookingAPIException(Exception):
    """Base exception class for booking API."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ClassNotFoundException(BookingAPIException):
    """Raised when a requested class is not found."""

    pass


class NoSlotsAvailableException(BookingAPIException):
    """Raised when no slots are available for booking."""

    pass


class InvalidBookingDataException(BookingAPIException):
    """Raised when booking data is invalid."""

    pass


class DuplicateBookingException(BookingAPIException):
    """Raised when trying to create a duplicate booking."""

    pass


def create_http_exception(
    status_code: int, message: str, details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create a standardized HTTP exception."""
    return HTTPException(
        status_code=status_code,
        detail={"message": message, "details": details or {}, "error_type": "booking_api_error"},
    )

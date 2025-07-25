"""
Pydantic schemas for request/response validation and serialization.
Implements comprehensive validation with custom validators.
"""

from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class BookingStatus(str, Enum):
    """Enumeration for booking status."""
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class ClassType(str, Enum):
    """Enumeration for class types."""
    YOGA = "Yoga"
    ZUMBA = "Zumba"
    HIIT = "HIIT"
    PILATES = "Pilates"
    CARDIO = "Cardio"


# Base schemas
class FitnessClassBase(BaseModel):
    """Base schema for fitness class."""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    instructor: str = Field(..., min_length=2, max_length=100)
    class_datetime: datetime
    duration_minutes: int = Field(default=60, ge=15, le=180)
    max_slots: int = Field(..., ge=1, le=50)
    
    @validator('class_datetime')
    def validate_future_datetime(cls, v):
        if v <= datetime.now():
            raise ValueError('Class datetime must be in the future')
        return v


class FitnessClassCreate(FitnessClassBase):
    """Schema for creating a fitness class."""
    pass


class FitnessClassResponse(FitnessClassBase):
    """Schema for fitness class response."""
    id: int
    available_slots: int
    booked_slots: int
    is_fully_booked: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    """Base schema for booking."""
    class_id: int = Field(..., ge=1)
    client_name: str = Field(..., min_length=2, max_length=100)
    client_email: EmailStr
    notes: Optional[str] = Field(None, max_length=500)


class BookingCreate(BookingBase):
    """Schema for creating a booking."""
    
    @validator('client_name')
    def validate_client_name(cls, v):
        if not v.strip():
            raise ValueError('Client name cannot be empty')
        return v.strip().title()


class BookingResponse(BookingBase):
    """Schema for booking response."""
    id: int
    booking_reference: str
    booking_status: BookingStatus
    created_at: datetime
    fitness_class: FitnessClassResponse
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Schema for booking list response."""
    bookings: List[BookingResponse]
    total_count: int
    client_email: str


# API Response schemas
class APIResponse(BaseModel):
    """Generic API response schema."""
    success: bool
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    message: str
    details: dict = {}
    error_type: str = "api_error"


# Query parameter schemas
class TimezoneQuery(BaseModel):
    """Schema for timezone query parameter."""
    timezone: Optional[str] = Field(None, description="Target timezone (e.g., 'America/New_York')")

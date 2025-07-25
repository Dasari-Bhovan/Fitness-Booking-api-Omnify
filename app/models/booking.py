"""
SQLAlchemy models for the fitness studio booking system.
Implements proper relationships, constraints, and indexing.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.db_utils import Base
from app.utils.timezone_utils import tz_manager


class FitnessClass(Base):
    """Model representing a fitness class."""

    __tablename__ = "fitness_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    instructor = Column(String(100), nullable=False)
    class_datetime = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    max_slots = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="fitness_class", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FitnessClass(id={self.id}, name='{self.name}', instructor='{self.instructor}')>"

    @property
    def booked_slots(self) -> int:
        """Calculate number of booked slots."""
        return self.max_slots - self.available_slots

    @property
    def is_fully_booked(self) -> bool:
        """Check if class is fully booked."""
        return self.available_slots <= 0

    @property
    def is_past(self) -> bool:
        """Check if class datetime has passed."""
        return self.class_datetime < datetime.now(tz=tz_manager.default_tz)


class Booking(Base):
    """Model representing a class booking."""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("fitness_classes.id"), nullable=False, index=True)
    client_name = Column(String(100), nullable=False)
    client_email = Column(String(100), nullable=False, index=True)
    booking_status = Column(String(20), default="confirmed", index=True)  # confirmed, cancelled
    booking_reference = Column(String(50), unique=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    fitness_class = relationship("FitnessClass", back_populates="bookings")

    def __repr__(self):
        return f"<Booking(id={self.id}, client_email='{self.client_email}', reference='{self.booking_reference}')>"

    @property
    def is_active(self) -> bool:
        """Check if booking is active (not cancelled)."""
        return self.booking_status == "confirmed"

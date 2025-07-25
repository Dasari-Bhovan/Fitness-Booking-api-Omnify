"""
Business logic service for handling booking operations.
Implements the core business rules and data processing logic.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.booking import FitnessClass, Booking
from ..schemas.booking import BookingCreate, FitnessClassCreate
from ..utils.exceptions import (
    ClassNotFoundException,
    NoSlotsAvailableException,
    DuplicateBookingException,
    InvalidBookingDataException
)
from ..utils.timezone_utils import tz_manager
import logging

logger = logging.getLogger(__name__)


class BookingService:
    """Service class handling all booking-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_classes(self, timezone: Optional[str] = None) -> List[FitnessClass]:
        """
        Retrieve all upcoming active fitness classes.
        
        Args:
            timezone: Target timezone for datetime conversion
            
        Returns:
            List of fitness classes
        """
        try:
            current_time = tz_manager.get_current_time()
            
            classes = self.db.query(FitnessClass).filter(
                and_(
                    FitnessClass.is_active == True,
                    FitnessClass.class_datetime > current_time
                )
            ).order_by(FitnessClass.class_datetime).all()
            
            # Convert timezone if requested
            if timezone and classes:
                for fitness_class in classes:
                    fitness_class.class_datetime = tz_manager.convert_timezone(
                        fitness_class.class_datetime, timezone
                    )
            
            logger.info(f"Retrieved {len(classes)} upcoming classes")
            return classes
            
        except Exception as e:
            logger.error(f"Error retrieving classes: {e}")
            raise
    
    def get_class_by_id(self, class_id: int) -> FitnessClass:
        """
        Get a specific fitness class by ID.
        
        Args:
            class_id: ID of the fitness class
            
        Returns:
            FitnessClass object
            
        Raises:
            ClassNotFoundException: If class is not found
        """
        fitness_class = self.db.query(FitnessClass).filter(
            FitnessClass.id == class_id,
            FitnessClass.is_active == True
        ).first()
        
        if not fitness_class:
            raise ClassNotFoundException(
                f"Class with ID {class_id} not found or inactive",
                {"class_id": class_id}
            )
        
        return fitness_class
    
    def create_booking(self, booking_data: BookingCreate) -> Booking:
        """
        Create a new booking for a fitness class.
        
        Args:
            booking_data: Booking creation data
            
        Returns:
            Created booking object
            
        Raises:
            ClassNotFoundException: If class doesn't exist
            NoSlotsAvailableException: If no slots available
            DuplicateBookingException: If duplicate booking exists
        """
        try:
            # Get the fitness class
            fitness_class = self.get_class_by_id(booking_data.class_id)
            
            # Check if class is in the past
            if fitness_class.is_past:
                raise InvalidBookingDataException(
                    "Cannot book a class that has already occurred",
                    {"class_datetime": fitness_class.class_datetime}
                )
            
            # Check available slots
            if fitness_class.available_slots <= 0:
                raise NoSlotsAvailableException(
                    f"No available slots for class '{fitness_class.name}'",
                    {
                        "class_id": booking_data.class_id,
                        "available_slots": fitness_class.available_slots
                    }
                )
            
            # Check for duplicate booking
            existing_booking = self.db.query(Booking).filter(
                and_(
                    Booking.class_id == booking_data.class_id,
                    Booking.client_email == booking_data.client_email,
                    Booking.booking_status == "confirmed"
                )
            ).first()
            
            if existing_booking:
                raise DuplicateBookingException(
                    f"Client {booking_data.client_email} already has a booking for this class",
                    {"existing_booking_id": existing_booking.id}
                )
            
            # Create booking
            booking_reference = self._generate_booking_reference()
            new_booking = Booking(
                class_id=booking_data.class_id,
                client_name=booking_data.client_name,
                client_email=booking_data.client_email,
                notes=booking_data.notes,
                booking_reference=booking_reference,
                booking_status="confirmed"
            )
            
            # Reduce available slots
            fitness_class.available_slots -= 1
            
            # Add to database
            self.db.add(new_booking)
            self.db.commit()
            self.db.refresh(new_booking)
            
            logger.info(f"Booking created successfully: {booking_reference}")
            return new_booking
            
        except (ClassNotFoundException, NoSlotsAvailableException, 
                DuplicateBookingException, InvalidBookingDataException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating booking: {e}")
            raise InvalidBookingDataException(f"Failed to create booking: {str(e)}")
    
    def get_bookings_by_email(self, client_email: str) -> List[Booking]:
        """
        Get all bookings for a specific client email.
        
        Args:
            client_email: Client's email address
            
        Returns:
            List of bookings
        """
        try:
            bookings = self.db.query(Booking).filter(
                Booking.client_email == client_email
            ).order_by(Booking.created_at.desc()).all()
            
            logger.info(f"Retrieved {len(bookings)} bookings for {client_email}")
            return bookings
            
        except Exception as e:
            logger.error(f"Error retrieving bookings for {client_email}: {e}")
            raise
    
    def create_sample_classes(self):
        """Create sample fitness classes for testing."""
        try:
            # Check if classes already exist
            existing_classes = self.db.query(FitnessClass).count()
            if existing_classes > 0:
                logger.info("Sample classes already exist")
                return
            
            # Create sample classes
            sample_classes = [
                {
                    "name": "Morning Yoga",
                    "description": "Start your day with peaceful yoga practice",
                    "instructor": "Sarah Johnson",
                    "class_datetime": tz_manager.get_current_time().replace(hour=8, minute=0, second=0, microsecond=0),
                    "duration_minutes": 60,
                    "max_slots": 15,
                    "available_slots": 15
                },
                {
                    "name": "High Energy Zumba",
                    "description": "Dance your way to fitness with energetic Zumba",
                    "instructor": "Carlos Rodriguez",
                    "class_datetime": tz_manager.get_current_time().replace(hour=18, minute=30, second=0, microsecond=0),
                    "duration_minutes": 45,
                    "max_slots": 20,
                    "available_slots": 20
                },
                {
                    "name": "HIIT Intensive",
                    "description": "High-intensity interval training for maximum results",
                    "instructor": "Mike Thompson",
                    "class_datetime": tz_manager.get_current_time().replace(hour=19, minute=0, second=0, microsecond=0),
                    "duration_minutes": 30,
                    "max_slots": 12,
                    "available_slots": 12
                }
            ]
            
            for class_data in sample_classes:
                fitness_class = FitnessClass(**class_data)
                self.db.add(fitness_class)
            
            self.db.commit()
            logger.info("Sample classes created successfully")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating sample classes: {e}")
            raise
    
    def _generate_booking_reference(self) -> str:
        """Generate a unique booking reference."""
        return f"FB{uuid.uuid4().hex[:8].upper()}"

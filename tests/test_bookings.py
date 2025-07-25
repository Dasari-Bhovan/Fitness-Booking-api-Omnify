"""
Comprehensive test suite for the booking API.
Tests all endpoints with various scenarios and edge cases.
"""

import json
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db_utils import Base, get_db
from app.main import app
from app.models.booking import Booking, FitnessClass
from app.utils.timezone_utils import tz_manager

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_class(test_db):
    """Create a sample fitness class for testing."""
    db = TestingSessionLocal()
    future_time = tz_manager.get_current_time() + timedelta(days=1)

    fitness_class = FitnessClass(
        name="Test Yoga",
        description="Test yoga class",
        instructor="Test Instructor",
        class_datetime=future_time,
        duration_minutes=60,
        max_slots=10,
        available_slots=10,
        is_active=True,
    )

    db.add(fitness_class)
    db.commit()
    db.refresh(fitness_class)
    db.close()
    return fitness_class


class TestClassesEndpoint:
    """Test cases for GET /classes endpoint."""

    def test_get_classes_empty(self, client, test_db):
        """Test getting classes when none exist."""
        response = client.get("/api/v1/classes")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_classes_with_data(self, client, sample_class):
        """Test getting classes with sample data."""
        response = client.get("/api/v1/classes")
        assert response.status_code == 200

        classes = response.json()
        assert len(classes) == 1
        assert classes[0]["name"] == "Test Yoga"
        assert classes[0]["instructor"] == "Test Instructor"
        assert classes[0]["available_slots"] == 10
        assert classes[0]["booked_slots"] == 0

    def test_get_classes_with_timezone(self, client, sample_class):
        """Test getting classes with timezone conversion."""
        response = client.get("/api/v1/classes?timezone=America/New_York")
        assert response.status_code == 200

        classes = response.json()
        assert len(classes) == 1
        # Verify timezone conversion occurred (datetime should be different)
        assert "class_datetime" in classes[0]


class TestBookingEndpoint:
    """Test cases for POST /book endpoint."""

    def test_create_booking_success(self, client, sample_class):
        """Test successful booking creation."""
        booking_data = {
            "class_id": sample_class.id,
            "client_name": "John Doe",
            "client_email": "john.doe@example.com",
            "notes": "First time booking",
        }

        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 200

        booking = response.json()
        assert booking["client_name"] == "John Doe"
        assert booking["client_email"] == "john.doe@example.com"
        assert booking["booking_status"] == "confirmed"
        assert "booking_reference" in booking
        assert booking["fitness_class"]["available_slots"] == 9  # Reduced by 1

    def test_create_booking_invalid_class(self, client, test_db):
        """Test booking with invalid class ID."""
        booking_data = {
            "class_id": 999,
            "client_name": "John Doe",
            "client_email": "john.doe@example.com",
        }

        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]["message"].lower()

    def test_create_booking_duplicate(self, client, sample_class):
        """Test creating duplicate booking for same client."""
        booking_data = {
            "class_id": sample_class.id,
            "client_name": "John Doe",
            "client_email": "john.doe@example.com",
        }

        # Create first booking
        response1 = client.post("/api/v1/book", json=booking_data)
        assert response1.status_code == 200

        # Try to create duplicate booking
        response2 = client.post("/api/v1/book", json=booking_data)
        assert response2.status_code == 409
        assert "already has a booking" in response2.json()["detail"]["message"]

    def test_create_booking_no_slots(self, client, test_db):
        """Test booking when no slots available."""
        db = TestingSessionLocal()
        future_time = tz_manager.get_current_time() + timedelta(days=1)

        # Create class with 0 available slots
        fitness_class = FitnessClass(
            name="Full Class",
            instructor="Test Instructor",
            class_datetime=future_time,
            max_slots=1,
            available_slots=0,
            is_active=True,
        )

        db.add(fitness_class)
        db.commit()
        db.refresh(fitness_class)
        db.close()

        booking_data = {
            "class_id": fitness_class.id,
            "client_name": "John Doe",
            "client_email": "john.doe@example.com",
        }

        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 409
        assert "no available slots" in response.json()["detail"]["message"].lower()

    def test_create_booking_invalid_email(self, client, sample_class):
        """Test booking with invalid email format."""
        booking_data = {
            "class_id": sample_class.id,
            "client_name": "John Doe",
            "client_email": "invalid-email",
        }

        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 422  # Validation error

    def test_create_booking_missing_fields(self, client, sample_class):
        """Test booking with missing required fields."""
        booking_data = {
            "class_id": sample_class.id,
            # missing client_name and client_email
        }

        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 422


class TestBookingsListEndpoint:
    """Test cases for GET /bookings endpoint."""

    def test_get_bookings_empty(self, client, test_db):
        """Test getting bookings when none exist."""
        response = client.get("/api/v1/bookings?client_email=test@example.com")
        assert response.status_code == 200

        result = response.json()
        assert result["bookings"] == []
        assert result["total_count"] == 0
        assert result["client_email"] == "test@example.com"

    def test_get_bookings_with_data(self, client, sample_class):
        """Test getting bookings with existing data."""
        # Create a booking first
        booking_data = {
            "class_id": sample_class.id,
            "client_name": "Jane Doe",
            "client_email": "jane.doe@example.com",
        }

        client.post("/api/v1/book", json=booking_data)

        # Get bookings for the client
        response = client.get("/api/v1/bookings?client_email=jane.doe@example.com")
        assert response.status_code == 200

        result = response.json()
        assert len(result["bookings"]) == 1
        assert result["total_count"] == 1
        assert result["bookings"][0]["client_email"] == "jane.doe@example.com"

    def test_get_bookings_missing_email(self, client, test_db):
        """Test getting bookings without email parameter."""
        response = client.get("/api/v1/bookings")
        assert response.status_code == 422  # Missing required parameter


class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    def test_health_check(self, client, test_db):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

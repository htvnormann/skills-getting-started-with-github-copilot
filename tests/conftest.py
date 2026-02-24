"""
Shared pytest configuration and fixtures for FastAPI tests.

Provides test client and activity data fixtures following AAA pattern principles.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for making API requests.
    
    Resets the activities database to a clean state before each test,
    ensuring test isolation.
    """
    # Reset activities to clean state before each test
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team and recreational play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["james@mergington.edu", "jessica@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and compete with robots",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science olympiad": {
            "description": "Compete in science competitions and experiments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        }
    })
    
    return TestClient(app)


@pytest.fixture
def full_activity():
    """Fixture providing activity data with maximum participants."""
    return {
        "name": "Chess Club",
        "max_participants": 12,
        "current_participants": 12
    }


@pytest.fixture
def empty_activity():
    """Fixture providing activity data with no participants."""
    return {
        "name": "Drama Club",
        "max_participants": 25,
        "current_participants": 1
    }


@pytest.fixture
def nonexistent_activity():
    """Fixture providing a name for an activity that doesn't exist."""
    return "Nonexistent Activity"


@pytest.fixture
def new_participant_email():
    """Fixture providing an email for a new participant."""
    return "newstudent@mergington.edu"


@pytest.fixture
def existing_participant_email():
    """Fixture providing an email of an existing participant."""
    return "michael@mergington.edu"

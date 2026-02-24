"""
Tests for GET /activities endpoint.

Tests follow AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and fixtures
- Act: Make the API call
- Assert: Verify the response
"""

import pytest


class TestGetActivities:
    """Test suite for retrieving all activities."""

    def test_get_activities_success(self, client):
        """
        Happy path: Get all activities returns status 200 with all activities.
        
        Arrange: Client fixture is ready
        Act: Make GET request to /activities
        Assert: Response is 200, contains expected activities and fields
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()

        # Verify response is a dictionary
        assert isinstance(activities_data, dict)

        # Verify expected activities are present
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert "Gym Class" in activities_data
        assert "Basketball Team" in activities_data
        assert "Tennis Club" in activities_data
        assert "Drama Club" in activities_data
        assert "Art Studio" in activities_data
        assert "Robotics Club" in activities_data
        assert "Science olympiad" in activities_data

    def test_get_activities_contains_required_fields(self, client):
        """
        Verify each activity contains required fields for frontend display.
        
        Arrange: Client fixture is ready
        Act: Get all activities
        Assert: Each activity has description, schedule, max_participants, participants
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert - Check Chess Club as representative activity
        chess_club = activities_data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

        # Verify field types and values
        assert isinstance(chess_club["description"], str)
        assert isinstance(chess_club["schedule"], str)
        assert isinstance(chess_club["max_participants"], int)
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_participant_count_accuracy(self, client):
        """
        Verify participant counts accurately reflect signup state.
        
        Arrange: Client fixture initialized with known participants
        Act: Get activities
        Assert: Participant count matches expected values
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert - Check initial participant counts
        assert len(activities_data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]

        assert len(activities_data["Programming Class"]["participants"]) == 2
        assert len(activities_data["Drama Club"]["participants"]) == 1
        assert len(activities_data["Basketball Team"]["participants"]) == 1

    def test_get_activities_returns_all_nine_activities(self, client):
        """
        Verify all nine activities are returned regardless of participant count.
        
        Arrange: Client fixture initialized
        Act: Get activities
        Assert: Exactly 9 activities returned
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        assert len(activities_data) == 9

    def test_activities_immutable_on_retrieval(self, client):
        """
        Happy path: Retrieving activities doesn't trigger side effects.
        
        Arrange: Initial state of activities
        Act: Make multiple GET requests
        Assert: Same data returned each time
        """
        # Act - First request
        response1 = client.get("/activities")
        data1 = response1.json()

        # Act - Second request
        response2 = client.get("/activities")
        data2 = response2.json()

        # Assert - Data should be identical
        assert data1 == data2
        assert len(data1["Chess Club"]["participants"]) == 2


class TestGetActivitiesEdgeCases:
    """Test edge cases for GET /activities endpoint."""

    def test_activities_description_format(self, client):
        """Verify activity descriptions are non-empty strings."""
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name, activity_data in activities_data.items():
            assert isinstance(activity_data["description"], str)
            assert len(activity_data["description"]) > 0

    def test_activities_schedule_format(self, client):
        """Verify activity schedules are non-empty strings."""
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name, activity_data in activities_data.items():
            assert isinstance(activity_data["schedule"], str)
            assert len(activity_data["schedule"]) > 0

    def test_activities_max_participants_valid_range(self, client):
        """Verify max_participants values are positive integers."""
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name, activity_data in activities_data.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_activities_participants_are_email_strings(self, client):
        """Verify participants are valid email-like strings."""
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name, activity_data in activities_data.items():
            participants = activity_data["participants"]
            for participant in participants:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation
                assert len(participant) > 0

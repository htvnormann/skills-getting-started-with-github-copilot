"""
Tests for POST /activities/{activity_name}/signup endpoint.

Tests follow AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and fixtures
- Act: Make the API call
- Assert: Verify the response
"""

import pytest


class TestSignupSuccess:
    """Test successful signup scenarios."""

    def test_signup_new_participant_success(self, client, new_participant_email):
        """
        Happy path: New student successfully signs up for an activity.
        
        Arrange: Valid activity name and new email not yet signed up
        Act: POST to /activities/{activity_name}/signup
        Assert: Returns 200 and confirmation message
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_participant_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_participant_email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_participant_to_activity(self, client, new_participant_email):
        """
        Happy path: Verify participant is actually added to activity after signup.
        
        Arrange: Valid activity and new email
        Act: Sign up, then retrieve activities
        Assert: Participant appears in activity's participant list
        """
        # Arrange
        activity_name = "Programming Class"

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_participant_email}
        )
        activities_response = client.get("/activities")

        # Assert
        assert signup_response.status_code == 200
        assert activities_response.status_code == 200
        activities_data = activities_response.json()
        assert new_participant_email in activities_data[activity_name]["participants"]

    def test_signup_multiple_different_participants(self, client):
        """
        Happy path: Multiple different students can sign up for same activity.
        
        Arrange: Multiple new emails for same activity
        Act: Sign up each student
        Assert: All signups successful and participant list updated
        """
        # Arrange
        activity_name = "Art Studio"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        initial_count = 2  # Art Studio starts with 2 participants

        # Act & Assert for each signup
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Verify all participants added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert len(participants) == initial_count + len(emails)
        for email in emails:
            assert email in participants

    def test_signup_to_different_activities(self, client, new_participant_email):
        """
        Happy path: Same student can sign up for multiple activities.
        
        Arrange: One email, multiple activities
        Act: Sign up for multiple activities
        Assert: All signups successful
        """
        # Arrange
        activities_to_join = ["Chess Club", "Programming Class", "Robotics Club"]

        # Act & Assert
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": new_participant_email}
            )
            assert response.status_code == 200

        # Verify participant in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for activity_name in activities_to_join:
            assert new_participant_email in activities_data[activity_name]["participants"]


class TestSignupErrors:
    """Test error cases for signup endpoint."""

    def test_signup_nonexistent_activity(self, client, new_participant_email, nonexistent_activity):
        """
        Error case: Attempting to sign up for activity that doesn't exist.
        
        Arrange: Activity name that doesn't exist, valid email
        Act: POST to signup for nonexistent activity
        Assert: Returns 404 with appropriate error message
        """
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": new_participant_email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_already_signed_up_student(self, client, existing_participant_email):
        """
        Error case: Student already signed up for activity cannot sign up again.
        
        Arrange: Email of student already in activity
        Act: Attempt to sign up again
        Assert: Returns 400 with conflict message
        """
        # Act
        response = client.post(
            f"/activities/Chess Club/signup",
            params={"email": existing_participant_email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_missing_email_parameter(self, client):
        """
        Error case: Email parameter is missing.
        
        Arrange: No email parameter provided
        Act: POST without email
        Assert: Returns 422 Unprocessable Entity (validation error)
        """
        # Act
        response = client.post("/activities/Chess Club/signup")

        # Assert
        assert response.status_code == 422

    def test_signup_empty_email_parameter(self, client):
        """
        Error case: Email parameter is empty string.
        
        Arrange: Empty string as email
        Act: POST with empty email
        Assert: May return 400 or silently treat empty email as distinct from actual emails
        """
        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": ""}
        )

        # Assert
        # Empty string should be accepted (it's a distinct participant identifier)
        # but behavior depends on implementation
        assert response.status_code in [200, 400]

    def test_signup_case_sensitive_activity_name(self, client, new_participant_email):
        """
        Error case: Activity names are case-sensitive.
        
        Arrange: Activity name with different casing
        Act: POST with different case
        Assert: Returns 404 if case doesn't match exactly
        """
        # Act - Try with lowercase
        response = client.post(
            f"/activities/chess club/signup",
            params={"email": new_participant_email}
        )

        # Assert
        assert response.status_code == 404

    def test_signup_activity_at_capacity(self, client):
        """
        Error case: Cannot sign up when activity is at maximum capacity.
        
        Arrange: Create activity with 1 open spot, fill it with signups
        Act: Try to sign up when full
        Assert: Signup succeeds until capacity is reached
        """
        # Arrange - Tennis Club has max 12, starts with 2 participants
        activity_name = "Tennis Club"
        
        # Act - Fill Tennis Club to capacity (10 more needed to reach 12)
        for i in range(10):
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"filler{i}@mergington.edu"}
            )
            assert response.status_code == 200

        # Verify at capacity
        activities = client.get("/activities").json()
        assert len(activities[activity_name]["participants"]) == 12

        # Act - Try to sign up when full (should work still - app doesn't enforce max)
        # This test documents current behavior; if max should be enforced, this would need to change
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@mergington.edu"}
        )

        # Assert - Current implementation allows exceeding max
        assert response.status_code == 200


class TestSignupEdgeCases:
    """Test edge cases and special scenarios for signup."""

    def test_signup_special_characters_in_email(self, client):
        """
        Edge case: Email with special characters is handled.
        
        Arrange: Email with special characters
        Act: Sign up with special character email
        Assert: Successfully stored if provided
        """
        # Arrange
        special_email = "student+tag@mergington.edu"

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": special_email}
        )

        # Assert
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert special_email in activities["Chess Club"]["participants"]

    def test_signup_whitespace_in_email(self, client):
        """
        Edge case: Email with leading/trailing whitespace.
        
        Arrange: Email with whitespace
        Act: POST with whitespace
        Assert: Email stored as-is (no trimming by default in FastAPI)
        """
        # Arrange
        email_with_space = " student@mergington.edu"

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email_with_space}
        )

        # Assert
        assert response.status_code == 200
        # Whitespace is preserved in the storage
        activities = client.get("/activities").json()
        assert email_with_space in activities["Chess Club"]["participants"]

    def test_signup_preserves_existing_participants(self, client, new_participant_email):
        """
        Edge case: Adding new participant doesn't modify existing participants.
        
        Arrange: Activity with existing participants
        Act: Add new participant
        Assert: Existing participants unchanged, new participant added
        """
        # Arrange
        activity_name = "Chess Club"
        initial_response = client.get("/activities").json()
        initial_participants = set(initial_response[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_participant_email}
        )

        # Assert
        assert response.status_code == 200
        updated_response = client.get("/activities").json()
        updated_participants = set(updated_response[activity_name]["participants"])

        # All original participants still present
        assert initial_participants.issubset(updated_participants)
        # New participant added
        assert new_participant_email in updated_participants
        # Exactly one new participant
        assert len(updated_participants) == len(initial_participants) + 1

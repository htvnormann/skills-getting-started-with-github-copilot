"""
Tests for POST /activities/{activity_name}/unregister endpoint.

Tests follow AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and fixtures
- Act: Make the API call
- Assert: Verify the response
"""

import pytest


class TestUnregisterSuccess:
    """Test successful unregister scenarios."""

    def test_unregister_existing_participant_success(self, client, existing_participant_email):
        """
        Happy path: Existing participant successfully unregisters from activity.
        
        Arrange: Participant already signed up for Chess Club
        Act: POST to /activities/{activity_name}/unregister
        Assert: Returns 200 and confirmation message
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert existing_participant_email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_removes_participant_from_activity(self, client, existing_participant_email):
        """
        Happy path: Verify participant is actually removed after unregister.
        
        Arrange: Participant in Chess Club
        Act: Unregister, then retrieve activities
        Assert: Participant no longer in activity's participant list
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Verify participant is there initially
        initial_response = client.get("/activities").json()
        assert existing_participant_email in initial_response[activity_name]["participants"]

        # Act
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant_email}
        )
        activities_response = client.get("/activities")

        # Assert
        assert unregister_response.status_code == 200
        assert activities_response.status_code == 200
        activities_data = activities_response.json()
        assert existing_participant_email not in activities_data[activity_name]["participants"]

    def test_unregister_multiple_participants_individually(self, client):
        """
        Happy path: Multiple participants can unregister from same activity.
        
        Arrange: Multiple participants in activity
        Act: Unregister each participant
        Assert: Each unregister succeeds and participant removed
        """
        # Arrange
        activity_name = "Chess Club"
        # Michael and Daniel are in Chess Club initially
        participants_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act & Assert
        for email in participants_to_remove:
            response = client.post(
                f"/activities/{activity_name}/unregister",
                params={"email": email}
            )
            assert response.status_code == 200

        # Verify both removed
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert len(participants) == 0

    def test_unregister_participant_from_one_activity_doesnt_affect_others(self, client):
        """
        Happy path: Unregistering from one activity doesn't affect other activities.
        
        Arrange: Participant signs up for multiple activities
        Act: Unregister from one activity
        Assert: Participant removed from one, still in others if signed up
        """
        # Arrange
        email = "flexible@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Studio"]

        # Sign up for multiple activities
        for activity in activities_to_join:
            client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )

        # Act - Unregister from Programming Class
        response = client.post(
            "/activities/Programming Class/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert email not in activities["Programming Class"]["participants"]
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Art Studio"]["participants"]

    def test_unregister_only_target_participant_removed(self, client):
        """
        Happy path: Unregistering one participant doesn't affect other participants.
        
        Arrange: Multiple participants in activity
        Act: Unregister one specific participant
        Assert: Only that participant removed, others remain
        """
        # Arrange
        activity_name = "Drama Club"
        new_email = "newdrama@mergington.edu"
        initial_response = client.get("/activities").json()
        initial_count = len(initial_response[activity_name]["participants"])

        # Sign up new participant
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        updated_response = client.get("/activities").json()
        updated_count = len(updated_response[activity_name]["participants"])
        assert updated_count == initial_count


class TestUnregisterErrors:
    """Test error cases for unregister endpoint."""

    def test_unregister_nonexistent_activity(self, client):
        """
        Error case: Attempting to unregister from activity that doesn't exist.
        
        Arrange: Activity name that doesn't exist, valid email
        Act: POST to unregister from nonexistent activity
        Assert: Returns 404 with appropriate error message
        """
        # Act
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "someone@mergington.edu"}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_not_signed_up_participant(self, client):
        """
        Error case: Participant not signed up for activity cannot unregister.
        
        Arrange: Email of student not in activity
        Act: Attempt to unregister
        Assert: Returns 400 with appropriate message
        """
        # Act
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_missing_email_parameter(self, client):
        """
        Error case: Email parameter is missing.
        
        Arrange: No email parameter provided
        Act: POST without email
        Assert: Returns 422 Unprocessable Entity (validation error)
        """
        # Act
        response = client.post("/activities/Chess Club/unregister")

        # Assert
        assert response.status_code == 422

    def test_unregister_empty_email_parameter(self, client):
        """
        Error case: Email parameter is empty string.
        
        Arrange: Empty string as email
        Act: POST with empty email
        Assert: Returns 400 if email not found
        """
        # Act
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": ""}
        )

        # Assert
        # Empty string is a valid parameter value but not in participants
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_case_sensitive_activity_name(self, client):
        """
        Error case: Activity names are case-sensitive for unregister too.
        
        Arrange: Activity name with different casing
        Act: POST with different case
        Assert: Returns 404 if case doesn't match exactly
        """
        # Act
        response = client.post(
            "/activities/chess club/unregister",
            params={"email": "michael@mergington.edu"}
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_twice_same_participant(self, client, existing_participant_email):
        """
        Error case: Cannot unregister same participant twice.
        
        Arrange: Participant in activity
        Act: Unregister once (succeeds), unregister again
        Assert: First succeeds, second fails with 400
        """
        # Arrange
        activity_name = "Chess Club"

        # Act - First unregister
        response1 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant_email}
        )
        assert response1.status_code == 200

        # Act - Second unregister (should fail)
        response2 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_participant_email}
        )

        # Assert
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"].lower()


class TestUnregisterEdgeCases:
    """Test edge cases and special scenarios for unregister."""

    def test_unregister_special_characters_in_email(self, client):
        """
        Edge case: Email with special characters can be unregistered if signed up.
        
        Arrange: Sign up with special character email, then unregister
        Act: Sign up and unregister with special character email
        Assert: Both operations succeed
        """
        # Arrange
        special_email = "student+special@mergington.edu"

        # Act - Sign up
        signup_response = client.post(
            "/activities/Chess Club/signup",
            params={"email": special_email}
        )
        assert signup_response.status_code == 200

        # Act - Unregister
        unregister_response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": special_email}
        )

        # Assert
        assert unregister_response.status_code == 200
        activities = client.get("/activities").json()
        assert special_email not in activities["Chess Club"]["participants"]

    def test_unregister_whitespace_email_consistency(self, client):
        """
        Edge case: Email with whitespace must match exactly to unregister.
        
        Arrange: Sign up with whitespace, attempt unregister with and without
        Act: Sign up with space, unregister with space, attempt without space
        Assert: First succeeds, second fails
        """
        # Arrange
        email_with_space = " student@mergington.edu"
        email_without_space = "student@mergington.edu"

        # Act - Sign up with space
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email_with_space}
        )

        # Act - Unregister with space (should succeed)
        unregister_response1 = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email_with_space}
        )
        assert unregister_response1.status_code == 200

    def test_unregister_then_signup_same_participant(self, client):
        """
        Edge case: Participant can sign up again after unregistering.
        
        Arrange: Participant already in activity
        Act: Unregister, then sign up again
        Assert: Both succeed and participant in activity after second signup
        """
        # Arrange
        email = "flexible@mergington.edu"
        activity_name = "Chess Club"

        # Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200

        # Act - Sign up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert signup_response.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_unregister_reduces_participant_count_accurately(self, client):
        """
        Edge case: Participant count decreases by exactly one after unregister.
        
        Arrange: Activity with known participant count
        Act: Unregister one participant
        Assert: Count reduced by exactly one
        """
        # Arrange
        activity_name = "Programming Class"
        initial = client.get("/activities").json()
        initial_count = len(initial[activity_name]["participants"])

        # Act
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": "emma@mergington.edu"}
        )

        # Assert
        updated = client.get("/activities").json()
        updated_count = len(updated[activity_name]["participants"])
        assert updated_count == initial_count - 1

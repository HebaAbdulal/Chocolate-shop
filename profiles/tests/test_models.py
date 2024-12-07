from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import UserProfile

class UserProfileModelTest(TestCase):
    """Test suite for the UserProfile model."""

    def test_user_profile_creation_signal(self):
        """
        Test that a UserProfile is automatically created
        when a new User is created.
        """
        user = User.objects.create_user(username="testuser", password="testpassword")
        profile = UserProfile.objects.get(user=user)

        self.assertEqual(profile.user, user)
        self.assertEqual(profile.name, "Test User")  # Default name assigned in the signal

    def test_user_profile_update_signal(self):
        """
        Test that the UserProfile is updated if it exists
        and a User is saved.
        """
        user = User.objects.create_user(username="testuser", password="testpassword")
        profile = UserProfile.objects.get(user=user)

        # Update the User instance
        user.first_name = "UpdatedFirstName"
        user.save()

        # Ensure the profile still exists and hasn't changed unintentionally
        updated_profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.id, updated_profile.id)
        self.assertEqual(updated_profile.user.first_name, "UpdatedFirstName")

    def test_user_profile_string_representation(self):
        """
        Test the __str__ method of the UserProfile model.
        """
        user = User.objects.create_user(username="testuser", password="testpassword")
        profile = UserProfile.objects.get(user=user)

        self.assertEqual(str(profile), "testuser")

    def test_user_profile_fields(self):
        """
        Test that the UserProfile fields accept valid data.
        """
        user = User.objects.create_user(username="testuser", password="testpassword")
        profile = UserProfile.objects.get(user=user)

        # Update fields with valid data
        profile.default_phone_number = "1234567890"
        profile.default_street_address1 = "123 Test St"
        profile.default_town_or_city = "Test City"
        profile.default_postcode = "12345"
        profile.default_county = "Test County"
        profile.save()

        updated_profile = UserProfile.objects.get(user=user)

        self.assertEqual(updated_profile.default_phone_number, "1234567890")
        self.assertEqual(updated_profile.default_street_address1, "123 Test St")
        self.assertEqual(updated_profile.default_town_or_city, "Test City")
        self.assertEqual(updated_profile.default_postcode, "12345")
        self.assertEqual(updated_profile.default_county, "Test County")

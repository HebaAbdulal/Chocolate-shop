from django.test import TestCase
from profiles.forms import UserProfileForm
from profiles.models import UserProfile
from django.contrib.auth.models import User


class TestUserProfileForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up a user and associated profile for testing."""
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.profile, _ = UserProfile.objects.get_or_create(
            user=cls.user,
            defaults={
                'name': "Test User",
                'default_phone_number': "1234567890",
                'default_postcode': "12345",
                'default_town_or_city': "Test City",
                'default_street_address1': "123 Test St",
                'default_street_address2': "Apartment 456",
                'default_county': "Test County",
            }
        )

    def test_form_valid_data(self):
        """Test the form with valid data."""
        form = UserProfileForm(data={
            'name': "Updated Test User",
            'default_phone_number': "9876543210",
            'default_postcode': "54321",
            'default_town_or_city': "Updated City",
            'default_street_address1': "456 Updated St",
            'default_street_address2': "Suite 789",
            'default_county': "Updated County",
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], "Updated Test User")

    def test_form_invalid_data(self):
        """Test the form with invalid data."""
        form = UserProfileForm(data={
            'name': "",  # Required field left blank
            'default_phone_number': "1234567890",
            'default_postcode': "12345",
            'default_town_or_city': "Test City",
            'default_street_address1': "123 Test St",
            'default_street_address2': "Apartment 456",
            'default_county': "Test County",
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)  # Ensure 'name' is in form errors

    def test_form_missing_required_fields(self):
        """Test the form with missing required fields."""
        form = UserProfileForm(data={
            'default_phone_number': "1234567890",
            # 'name' is missing
            'default_postcode': "12345",
            'default_town_or_city': "Test City",
            'default_street_address1': "123 Test St",
            'default_street_address2': "Apartment 456",
            'default_county': "Test County",
        })
        self.assertFalse(form.is_valid(), f"Form unexpectedly valid: {form.errors}")
        self.assertIn('name', form.errors, f"'name' not in errors: {form.errors}")

    def test_form_placeholder_classes(self):
        """Test that placeholders and CSS classes are applied."""
        form = UserProfileForm()
        for field_name, field in form.fields.items():
            if field_name != 'default_country':
                self.assertIn('placeholder', field.widget.attrs)
                self.assertIn('class', field.widget.attrs)
                self.assertEqual(field.widget.attrs['class'], 'border-brown rounded-0 profile-form-input')

from django.test import TestCase
from checkout.forms import OrderForm
from checkout.models import Order
from django.contrib.auth.models import User
from profiles.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist


class OrderFormTests(TestCase):

    def setUp(self):
        """
        Set up test data, including a user and user profile.
        """
        # Create a user and profile
        self.user = User.objects.create_user(username="testuser", password="password")
        try:
            self.profile = UserProfile.objects.get(user=self.user)
        except UserProfile.DoesNotExist:
            self.profile = UserProfile.objects.create(user=self.user, name="Test User")

        # Create a valid order (not saved yet)
        self.order_data = {
            "full_name": "Test User",
            "email": "testuser@example.com",
            "phone_number": "123456789",
            "street_address1": "123 Test St",
            "street_address2": "",
            "town_or_city": "Test City",
            "postcode": "12345",
            "country": "US",
            "county": "Test County"
        }

    def test_order_form_valid(self):
        """Test the form with valid data."""
        form = OrderForm(data=self.order_data)
        self.assertTrue(form.is_valid())

    def test_order_form_invalid_missing_required(self):
        """Test the form with missing required fields."""
        invalid_data = self.order_data.copy()
        del invalid_data['full_name']  # Remove required field to make form invalid
        form = OrderForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('full_name', form.errors)

    def test_order_form_with_prefill(self):
        """Test the form with a pre-filled 'full_name' from user profile."""
        form = OrderForm(data=self.order_data, user_profile=self.profile)
        self.assertTrue(form.is_valid())
        # Check that 'full_name' was set in the form's initial data
        self.assertEqual(form.initial.get('full_name'), self.profile.name)


    def test_order_form_placeholders(self):
        """Test the form fields contain the correct placeholders."""
        form = OrderForm(data=self.order_data)
        placeholders = {
            'full_name': 'Full Name *',
            'email': 'Email Address *',
            'phone_number': 'Phone Number *',
            'postcode': 'Postal Code *',
            'town_or_city': 'Town or City *',
            'street_address1': 'Street Address 1 *',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }
        for field, expected_placeholder in placeholders.items():
            actual_placeholder = form.fields[field].widget.attrs['placeholder']
            self.assertEqual(actual_placeholder, expected_placeholder)




    def test_order_form_class_attribute(self):
        """Test if the correct CSS class is applied to form fields."""
        form = OrderForm(data=self.order_data)
        for field in form.fields:
            self.assertEqual(form.fields[field].widget.attrs['class'], 'stripe-style-input')

    def test_order_form_invalid_email(self):
        """Test form with invalid email address format."""
        invalid_data = self.order_data.copy()
        invalid_data['email'] = 'invalid-email'
        form = OrderForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_order_form_valid_with_optional_fields(self):
        """Test the form with optional fields like street_address2 left empty."""
        valid_data = self.order_data.copy()
        valid_data['street_address2'] = ""
        form = OrderForm(data=valid_data)
        self.assertTrue(form.is_valid())

    def test_order_form_create_order(self):
        """Test that valid form data creates an Order instance."""
        form = OrderForm(data=self.order_data)
        self.assertTrue(form.is_valid())
        order = form.save()  # Simulate saving the form data
        self.assertIsInstance(order, Order)
        self.assertEqual(order.full_name, self.order_data['full_name'])
        self.assertEqual(order.email, self.order_data['email'])

    def test_order_form_invalid_postcode(self):
        """Test that invalid postcode format makes the form invalid."""
        invalid_data = self.order_data.copy()
        invalid_data['postcode'] = '12'
        form = OrderForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('postcode', form.errors)

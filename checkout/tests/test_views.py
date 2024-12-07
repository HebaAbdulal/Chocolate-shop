from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product, Category
from profiles.models import UserProfile
from checkout.models import Order
from unittest.mock import patch
import stripe

class CheckoutTests(TestCase):
    def setUp(self):
        """
        Set up test data.
        """
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="password")

        # Check if a profile exists or create one
        self.profile, created = UserProfile.objects.get_or_create(user=self.user)

        # Create a test category (necessary for Product)
        self.category = Category.objects.create(name="Test Category")

        # Create a test product and assign the category
        self.product = Product.objects.create(
            name="Test Product",
            price=10.00,
            category=self.category  # Assign category to product
        )

        # Set up the client
        self.client = Client()

        # Add product to session bag
        session = self.client.session
        session["bag"] = {str(self.product.id): 1}
        session.save()

    def test_checkout_view_get(self):
        """
        Test the checkout view (GET request) returns 200 status.
        """
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 200)

    def test_checkout_view_post(self):
        """
        Test the checkout view (POST request) returns 302 redirect to success on valid form data.
        """
        self.client.login(username="testuser", password="password")
        data = {
            "full_name": "Test User",
            "email": "testuser@example.com",
            "phone_number": "123456789",
            "country": "US",
            "postcode": "12345",
            "town_or_city": "Test City",
            "street_address1": "123 Test St",
            "street_address2": "",
            "county": "Test County",
            "client_secret": "valid_test_secret",
        }
        response = self.client.post(reverse("checkout"), data)
        self.assertEqual(response.status_code, 302)

    @patch("stripe.PaymentIntent.create")
    def test_cache_checkout_data(self, mock_create_payment_intent):
        """
        Test the cache_checkout_data view returns 200 status.
        """
        # Mock Stripe API response to create a payment intent
        mock_create_payment_intent.return_value = stripe.PaymentIntent(
            id="pi_3QSdTcH5lYVpNHaI1OdqhBz2",  # Use a valid PaymentIntent ID
            client_secret="pi_3QSdTcH5lYVpNHaI1OdqhBz2_secret_f94Fvef2z2hH5LKXlAnYRWDhl",  # Corresponding client_secret
            amount=1450,
            currency="usd"
        )

        self.client.login(username="testuser", password="password")
        response = self.client.post(
            reverse("cache_checkout_data"),
            {
                "client_secret": "pi_3QSdTcH5lYVpNHaI1OdqhBz2_secret_f94Fvef2z2hH5LKXlAnYRWDhl",  # Matching client_secret from mock
            }
        )
        print(response.content)  # Print the response content for debugging
        self.assertEqual(response.status_code, 200)


    def test_checkout_success_view(self):
        """
        Test the checkout_success view returns 200 status.
        """
        # Create a fake order for testing
        order = Order.objects.create(
            full_name="Test User",
            email="testuser@example.com",
            phone_number="123456789",
            country="US",
            postcode="12345",
            town_or_city="Test City",
            street_address1="123 Test St",
            county="Test County",
            stripe_pid="test_pid",
            original_bag="{}",
        )
        response = self.client.get(reverse("checkout_success", args=[order.order_number]))
        self.assertEqual(response.status_code, 200)

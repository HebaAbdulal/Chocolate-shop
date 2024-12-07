from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from profiles.models import UserProfile
from checkout.models import Order

class TestProfileViews(TestCase):
    def setUp(self):
        """Set up a user, profile, and an order for testing."""
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Retrieve the associated UserProfile (if it is auto-created by signals or overridden save)
        self.profile = UserProfile.objects.get(user=self.user)

        # Log in the user for authenticated views
        self.client.login(username='testuser', password='testpassword')

        # Create a test order
        self.order = Order.objects.create(
            user_profile=self.profile,
            full_name="Test User",
            email="testuser@example.com",
            phone_number="1234567890",
            country="US",
            town_or_city="Test City",
            street_address1="123 Test St",
            postcode="12345",
            original_bag="Test Bag",
            stripe_pid="stripe_pid_test",
            order_total=100.00,
            grand_total=120.00,
        )

    def test_profile_view_status_code(self):
        """Test that the profile view returns a 200 status code."""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')

    def test_order_history_view_status_code(self):
        """Test that the order history view returns a 200 status code."""
        response = self.client.get(reverse('order_history', args=[self.order.order_number]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout_success.html')

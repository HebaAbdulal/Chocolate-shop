from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category

class TestBagViews(TestCase):
    """Test suite for bag views."""

    @classmethod
    def setUpTestData(cls):
        """Set up a test category and product for use in the views."""
        cls.category = Category.objects.create(
            name="Test Category",
            friendly_name="Test Friendly Name",
        )
        cls.product = Product.objects.create(
            name="Test Product",
            description="A test product description.",
            price=10.00,
            category=cls.category,  # Associate the product with the category
        )
        cls.client = Client()

    def test_view_bag(self):
        """Test the view_bag view."""
        response = self.client.get(reverse('view_bag'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bag/bag.html')

    def test_add_to_bag(self):
        """Test the add_to_bag view."""
        response = self.client.post(
            reverse('add_to_bag', args=[self.product.id]),
            data={'quantity': 1, 'redirect_url': reverse('view_bag')}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after adding to bag
        self.assertIn(str(self.product.id), self.client.session['bag'])  # Product added to bag

    def test_adjust_bag(self):
        """Test the adjust_bag view."""
        # Add item to the session first
        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()

        response = self.client.post(
            reverse('adjust_bag', args=[self.product.id]),
            data={'quantity': 2}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after adjusting
        self.assertEqual(self.client.session['bag'][str(self.product.id)], 2)  # Quantity updated

    def test_remove_from_bag(self):
        """Test the remove_from_bag view."""
        # Add item to the session first
        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()

        response = self.client.post(reverse('remove_bag', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)  # Success status
        self.assertNotIn(str(self.product.id), self.client.session['bag'])  # Product removed

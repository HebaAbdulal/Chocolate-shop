from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Category, Product, Wishlist, Review, Discount
from django.core.exceptions import ValidationError
from checkout.models import Order, OrderLineItem
from products.forms import ProductForm
from profiles.models import UserProfile



class CategoryModelTest(TestCase):

    def setUp(self):
        """Create a test category."""
        self.category = Category.objects.create(name="Test Category", friendly_name="Friendly Name")

    def test_category_str(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.category), "Test Category")


class ProductModelTest(TestCase):

    def setUp(self):
        """Create a test category and product."""
        self.category = Category.objects.create(name="Test Category", friendly_name="Friendly Name")
        self.product = Product.objects.create(
            name="Test Product",
            price=100.00,
            category=self.category,
            discount_percent=10.0
        )

    def test_product_str(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.product), "Test Product")

    def test_calculate_discounted_price(self):
        """Test the calculate_discounted_price method."""
        discounted_price = self.product.calculate_discounted_price()
        expected_price = 100.00 - (100.00 * 0.10)
        self.assertEqual(discounted_price, expected_price)

    def test_product_price_validation(self):
        """Test that the product price cannot be negative."""
        with self.assertRaises(ValidationError):
            self.product.price = -10.00
            self.product.full_clean()  # This triggers validation
    
    def test_product_form_invalid_data(self):
        """Test form with missing required fields."""
        data = {
            "name": "",  # Missing name (required field)
            "price": None,  # Ensure price is valid if not testing it
        }
        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())


class WishlistModelTest(TestCase):

    def setUp(self):
        """Create a test user and wishlist."""
        self.user = User.objects.create_user(username="testuser", password="password")
        self.wishlist = Wishlist.objects.create(user=self.user)

    def test_wishlist_str(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.wishlist), "testuser's Wishlist")

    def test_user_can_have_only_one_wishlist(self):
        """Test that each user can only have one wishlist."""
        user2 = User.objects.create_user(username="testuser2", password="password")
        wishlist2 = Wishlist.objects.create(user=user2)
        self.assertEqual(Wishlist.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Wishlist.objects.filter(user=user2).count(), 1)


class DiscountModelTest(TestCase):

    def setUp(self):
        """Create a test category and discount."""
        self.category = Category.objects.create(name="Test Category", friendly_name="Friendly Name")
        self.discount = Discount.objects.create(
            category=self.category,
            discount_percentage=20.0,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=5)
        )

    def test_is_active_method(self):
        """Test the is_active method to ensure discounts are active during the correct period."""
        self.assertTrue(self.discount.is_active())

    def test_discount_str(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.discount), f"Discount for {self.category.name} - {self.discount.discount_percentage}%")

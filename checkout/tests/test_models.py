from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import UserProfile
from products.models import Product, Category
from checkout.models import Order, OrderLineItem
from django.conf import settings


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile, created = UserProfile.objects.get_or_create(user=self.user, name="Test User")
        
        # Ensure a category exists
        category = Category.objects.create(name="Test Category")
        
        # Create a product with a category
        self.product = Product.objects.create(
            name="Test Product", 
            price=Decimal("10.00"), 
            sku="TEST123", 
            category=category  # Provide category here
        )

    def test_update_total_method(self):
        """Test that the update_total method updates the order totals correctly."""
        # Create order without line items initially
        order = Order.objects.create(
            user_profile=self.profile,
            full_name="Test User",
            email="testuser@example.com",
            phone_number="1234567890",
            country="US",
            town_or_city="Test City",
            street_address1="123 Test St",
            postcode="12345",
            order_total=Decimal("0.00"),  # Set order_total to 0 initially
            grand_total=Decimal("0.00"),  # Set grand_total to 0 initially
            original_bag="Test Bag",
            stripe_pid="stripe_pid_test"
        )
        
        # Create line item
        order_line_item = OrderLineItem.objects.create(order=order, product=self.product, quantity=2)

        # Assert that after creating the line item, order_total and grand_total are updated correctly
        self.assertEqual(order.order_total, Decimal("20.00"))  # 2 * 10 (price of product)
        self.assertEqual(order.grand_total, Decimal("24.50"))  # 20 + delivery cost (example delivery cost of 4.50)

        # Call update_total() method
        order.update_total()

        # After update, ensure the totals remain the same if no changes were made to line items or delivery costs
        self.assertEqual(order.order_total, Decimal("20.00"))  # 2 * 10 (price of product)
        self.assertEqual(order.grand_total, Decimal("24.50"))  # 20 + delivery cost (example delivery cost of 4.50)

class OrderLineItemModelTest(TestCase):
    def setUp(self):
        """Create a test user, user profile, and a product."""
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile, created = UserProfile.objects.get_or_create(user=self.user, name="Test User")
        category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", price=Decimal("10.00"), sku="TEST123", category=category)
        self.order = Order.objects.create(
            user_profile=self.profile,
            full_name="Test User",
            email="testuser@example.com",
            phone_number="1234567890",
            country="US",
            town_or_city="Test City",
            street_address1="123 Test St",
            postcode="12345",
            order_total=Decimal("100.00"),
            grand_total=Decimal("120.00"),
            original_bag="Test Bag",
            stripe_pid="stripe_pid_test"
        )

    def test_lineitem_total_calculation(self):
        """Test that the lineitem_total is calculated correctly when saving an order line item."""
        order_line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3
        )
        self.assertEqual(order_line_item.lineitem_total, Decimal("30.00"))  # 3 * 10 (price of product)

    def test_save_method_updates_lineitem_total(self):
        """Test that the save method correctly updates the lineitem_total."""
        order_line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )
        # Check initial lineitem_total
        self.assertEqual(order_line_item.lineitem_total, Decimal("20.00"))
        
        # Update the quantity
        order_line_item.quantity = 5
        order_line_item.save()
        
        # Check updated lineitem_total
        self.assertEqual(order_line_item.lineitem_total, Decimal("50.00"))  # 5 * 10 (price of product)

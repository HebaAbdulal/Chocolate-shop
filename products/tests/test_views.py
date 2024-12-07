from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, Category, Wishlist


class ProductViewsTest(TestCase):

    def setUp(self):
        """Create a test user, category, and product."""
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user.is_superuser = True  # Make the test user a superuser for edit and delete access
        self.user.save()  # Save the superuser status
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=self.category
        )
        self.add_product_url = reverse('add_product')
        self.edit_product_url = reverse('edit_product', kwargs={'product_id': self.product.id})
        self.product_list_url = reverse('products')

    def test_add_product_get(self):
        """Test the GET request to add a new product"""
        # Log in the test user
        login_success = self.client.login(username='testuser', password='password')
        self.assertTrue(login_success, "Login failed")  # Ensure user is logged in
        
        response = self.client.get(self.add_product_url)
        
        if response.status_code == 302:  # If the response is a redirect, print the location
            print("Redirected to:", response['Location'])
        
        self.assertEqual(response.status_code, 200)

    def test_edit_product_get(self):
        """Test the GET request to edit an existing product"""
        # Log in the test user
        login_success = self.client.login(username='testuser', password='password')
        self.assertTrue(login_success, "Login failed")  # Ensure user is logged in
        
        response = self.client.get(self.edit_product_url)
        
        if response.status_code == 302:  # If the response is a redirect, print the location
            print("Redirected to:", response['Location'])
        
        self.assertEqual(response.status_code, 200)

    def test_product_list_get(self):
        """Test the GET request to view the product list"""
        # Log in the test user
        login_success = self.client.login(username='testuser', password='password')
        self.assertTrue(login_success, "Login failed")  # Ensure user is logged in
        
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, 200)


class WishlistViewsTest(TestCase):

    def setUp(self):
        """Create a test user, a category, and products for the wishlist."""
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create a test category and products
        self.category = Category.objects.create(name="Test Category")
        self.product_1 = Product.objects.create(name="Product 1", description="Desc 1", price=29.99, category=self.category)
        self.product_2 = Product.objects.create(name="Product 2", description="Desc 2", price=49.99, category=self.category)

        # Create a wishlist and associate it with the user
        self.wishlist = Wishlist.objects.create(user=self.user)
        self.user.wishlist = self.wishlist
        self.user.save()

        # URL for viewing the wishlist
        self.wishlist_url = reverse('view_wishlist')  # This URL name is correct as per your urls.py

    def test_wishlist_view_get(self):
        """Test the GET request to view the wishlist"""
        # Log in the test user
        login_success = self.client.login(username='testuser', password='password')
        self.assertTrue(login_success, "Login failed")  # Ensure user is logged in

        # Add products to the wishlist
        self.user.wishlist.products.add(self.product_1, self.product_2)

        # Make a GET request to the wishlist page
        response = self.client.get(self.wishlist_url)

        # Assert the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_wishlist_empty_get(self):
        """Test the GET request when the wishlist is empty"""
        # Log in the test user
        login_success = self.client.login(username='testuser', password='password')
        self.assertTrue(login_success, "Login failed")  # Ensure user is logged in

        # Make a GET request to the wishlist page
        response = self.client.get(self.wishlist_url)

        # Assert the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)
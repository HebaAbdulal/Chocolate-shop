from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from products.models import Product, Category, Review
from products.forms import ProductForm, AddToWishlistForm, ReviewForm
from django.urls import reverse  # Add reverse import

class ProductFormTest(TestCase):

    def setUp(self):
        """Create a test user, category, and product for testing."""
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name="Test Category", friendly_name="Test Friendly Name")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=self.category
        )

    def test_product_form_valid_data(self):
        """Test valid form submission for ProductForm"""
        form_data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 50.0,
            'category': self.category.id,
            'discount_percent': 10.0,  # Add discount_percent if required
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)  # Print form errors if any

    def test_product_form_invalid_data(self):
        """Test form with missing required fields"""
        form_data = {
            'name': '',
            'description': 'Missing name',
            'price': '',
            'category': self.category.id,
            'discount_percent': 10.0,  # Add discount_percent if required
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('price', form.errors)

    def test_product_form_image_field(self):
        """Test form with an image file"""
        # Prepare a dummy image to simulate an image upload
        image_data = SimpleUploadedFile("test_image.jpg", b"fake image data", content_type="image/jpeg")

        form_data = {
            'name': 'New Product with Image',
            'description': 'Product with an image',
            'price': 50.0,
            'category': self.category.id,
            'discount_percent': 10.0,  # Add discount_percent if required
            'image': image_data,  # Simulate the image upload
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)  # Print form errors if any


class AddToWishlistFormTest(TestCase):

    def setUp(self):
        """Create a test user and product."""
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=Category.objects.create(name="Test Category", friendly_name="Test Friendly Name")
        )
        self.url = reverse('add_to_wishlist', kwargs={'product_id': self.product.id})

    def test_add_to_wishlist_form_valid(self):
        """Test the AddToWishlistForm with a valid product ID"""
        form_data = {
            'product_id': self.product.id,
        }
        form = AddToWishlistForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_add_to_wishlist_form_invalid(self):
        """Test the AddToWishlistForm with an invalid product ID"""
        form_data = {
            'product_id': 'invalid',
        }
        form = AddToWishlistForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('product_id', form.errors)


class ReviewFormTest(TestCase):

    def setUp(self):
        """Create a test user, product, and review for testing."""
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name="Test Category", friendly_name="Test Friendly Name")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=self.category
        )
        self.review = Review.objects.create(
            review_text="Great product!",
            product=self.product,
            user=self.user
        )

    def test_review_form_valid(self):
        """Test valid form submission for ReviewForm"""
        form_data = {
            'review_text': 'Amazing product!',
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid(self):
        """Test invalid form submission for ReviewForm (empty review)"""
        form_data = {
            'review_text': '',
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('review_text', form.errors)

    def test_review_form_widget(self):
        """Test the ReviewForm textarea widget"""
        form = ReviewForm()
        self.assertIn('<textarea', str(form['review_text']))  # Check if it's rendered as a textarea

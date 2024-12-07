from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone  # Added timezone import


class Category(models.Model):
    """
    A model representing product categories in the system.

    """
    class Meta:
        verbose_name_plural = 'Categories'
    name = models.CharField(max_length=100)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    A model representing a product in the store.
    """
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="No description available")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        help_text="Discount percentage (e.g., 10 for 10%)"
    )

    def __str__(self):
        return self.name

    def calculate_discounted_price(self):
        """Calculate price after applying the discount."""
        if self.discount_percent > 0:
            discount = self.price * (self.discount_percent / 100)
            return self.price - discount
        return self.price

    def clean(self):
        if self.price is not None and self.price < 0:
            raise ValidationError("Price cannot be negative.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    """
    A model representing a user's wishlist, containing favorite products.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField(Product, related_name="wishlists")

    def __str__(self):
        return f"{self.user.username}'s Wishlist"


class Review(models.Model):

    STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_text = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='approved')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # In products/models.py
def clean(self):
    OrderLineItem = apps.get_model('checkout', 'OrderLineItem')  # Dynamically fetch model
    if not OrderLineItem.objects.filter(order__user=self.user, product=self.product).exists():
        raise ValidationError("You can only review products you have purchased.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Discount(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="discounts")
    discount_percentage = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"Discount for {self.category.name} - {self.discount_percentage}%"

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

from django.db import models

class Category(models.Model):
    """
    A model representing product categories in the system.

    """
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=100)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    A model representing a product in the store.
    """
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="No description available")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return self.name



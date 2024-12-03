# products/templatetags/custom_filters.py
from django import template
from products.utils import calculate_discounted_price
from decimal import Decimal

register = template.Library()

@register.filter
def calculate_discounted_price_filter(product):
    """
    Custom filter to calculate the discounted price for a product.
    """
    return calculate_discounted_price(product)

@register.filter
def calc_discounted_total(bag_items):
    total = Decimal('0.00')  # Now the Decimal is correctly imported
    for item in bag_items:
        # Access the product from the dictionary
        product = item['product']
        # Calculate the discounted price
        discounted_price = calculate_discounted_price(product)
        # Add the price times quantity to the total
        total += discounted_price * item['quantity']
    return total

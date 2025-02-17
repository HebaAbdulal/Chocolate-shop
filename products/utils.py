from .models import Discount
from django.utils import timezone
from decimal import Decimal


def calculate_discounted_price(product):
    """
    Calculate the discounted price for a product based on active discounts.
    Args:
    product (Product): The product object.
    Returns:
    float: The discounted price if a discount is applicable,
    otherwise the original price.
    """
    discounts = Discount.objects.filter(
        category=product.category,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )

    if discounts.exists():
        discount = discounts.first()
        # Convert discount percentage to Decimal for accurate calculation
        discounted_price = product.price * (
            1 - Decimal(discount.discount_percentage) / Decimal(100)
        )
        return round(discounted_price, 2)

    return product.price

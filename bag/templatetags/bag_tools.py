from django import template

register = template.Library()


@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    """
    Calculates the subtotal for a given price and quantity.
    Assumes the price is the discounted price if a discount is applied.
    """
    return price * quantity


@register.filter(name='calculate_discounted_price_filter')
def calculate_discounted_price_filter(product):
    """
    Returns the discounted price of a product if applicable,
    otherwise the original price.
    """
    try:
        return product.calculate_discounted_price()
    except AttributeError:
        return product.price

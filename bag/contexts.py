from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product  # Assuming products are stored in Product model

def bag_contents(request):
    bag = request.session.get('bag', {})
    
    bag_items = []
    total = Decimal('0.00')
    product_count = 0
    standard_delivery = Decimal(str(settings.STANDARD_DELIVERY))  # Convert to Decimal

    for item_id, item_data in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        
        if isinstance(item_data, int):
            quantity = item_data
            total += quantity * product.price
            product_count += quantity
            bag_items.append({
                'item_id': item_id,
                'quantity': quantity,
                'product': product,
            })
        else:
            for size, quantity in item_data['items_by_size'].items():
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
                })

    delivery = standard_delivery if total > 0 else Decimal('0.00')
    grand_total = total + delivery

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'grand_total': grand_total,
    }

    return context

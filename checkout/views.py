from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm


def checkout(request):
    # Correct the session key to be a string
    bag = request.session.get("bag", {})
    
    # Check if the bag is empty and redirect if so
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment.")
        return redirect(reverse('products'))  # Fix typo in `reverse`
    
    # Initialize the order form
    order_form = OrderForm()
    
    # Render the checkout page with the order form
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51QK56rH5lYVpNHaIiXsmiT8JiUaWOOasNdQwlVuoMsJ9y3XQe2b7DaRx2d7EvcNXY82nTFCegBDPORF4iz9vWD0000zD18YeFW',
        'client_secret': 'test client secret'
    }
    return render(request, template, context)

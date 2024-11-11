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
    }
    return render(request, template, context)

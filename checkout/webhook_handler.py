import json
import time
import logging
import stripe
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from stripe.error import SignatureVerificationError
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

logger = logging.getLogger(__name__)


def my_webhook_view(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        # Verify the webhook signature using your Stripe secret
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the event here, e.g., payment_intent.succeeded, etc.
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Process the successful payment

    return JsonResponse({'status': 'success'})


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request
        logger.info("Webhook handler initialized.")

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        print("Attempting to send confirmation email...")
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order}
        )
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL}
        )

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [cust_email]
            )
            print(f"Email sent successfully to {cust_email}")
        except Exception as e:
            print(f"Error sending email: {e}")

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        logger.info(f"Unhandled event received: {event['type']}")
        print(f"Unhandled event type: {event['type']}")
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        print("Payment succeeded webhook received.")
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info
        print(f"PaymentIntent ID: {pid}, Bag: {bag}, Save Info: {save_info}")

        # Step 1: Retrieve the Payment Method
        payment_method = stripe.PaymentMethod.retrieve(intent.payment_method)
        billing_details = payment_method.billing_details
        print(f"Billing details retrieved: {billing_details}")

        # Step 2: Retrieve the Charge object
        stripe_charge = stripe.Charge.retrieve(intent.latest_charge)
        grand_total = round(stripe_charge.amount / 100, 2)
        print(f"Charge object retrieved, Grand Total: {grand_total}")

        shipping_details = intent.shipping
        print(f"Shipping details: {shipping_details}")

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None
        print("Cleaned shipping details:", shipping_details)

        # Update profile information if save_info was checked
        profile = None
        username = intent.metadata.username
        print(f"Username: {username}")
        if username != 'AnonymousUser':
            try:
                profile = UserProfile.objects.get(user__username=username)
                print("User profile retrieved:", profile)
                if save_info:
                    profile.default_full_name = shipping_details.name
                    profile.default_email = billing_details.email
                    profile.default_phone_number = shipping_details.phone
                    profile.default_country = shipping_details.address.country
                    profile.default_postcode = (
                        shipping_details.address.postal_code
                    )
                    profile.default_town_or_city = (
                        shipping_details.address.city
                    )
                    profile.default_street_address1 = (
                        shipping_details.address.line1
                    )
                    profile.default_street_address2 = (
                        shipping_details.address.line2
                    )
                    profile.default_county = shipping_details.address.state
                    profile.save()
                    print("User profile updated with shipping details.")
            except UserProfile.DoesNotExist:
                print(f"No profile found for username: {username}")

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                print(f"Order found in database: {order}")
                break
            except Order.DoesNotExist:
                print(f"Order not found. Attempt {attempt} of 5.")
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]} | '
                    f'SUCCESS: Verified order already in database'
                ),
                status=200
            )
        else:
            print("Order not found after 5 attempts. Creating a new order.")
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                print(f"Order created: {order}")
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                        print(f"Order line item created: {order_line_item}")
            except Exception as e:
                if order:
                    order.delete()
                print(f"Error creating order: {e}")
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | '
                    F'SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        print("Payment failed webhook received.")
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

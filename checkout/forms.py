from django import forms 
from .models import Order


class OrderForm(forms.ModelForm):
    """ A form for capturing order details """

    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders, classes, and optionally prefill
        'full_name' if provided via kwargs.
        """
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }

        # Autofocus on the first field
        self.fields['full_name'].widget.attrs['autofocus'] = True

        # Add placeholders and class styling
        for field in self.fields:
            if field != 'country':
                placeholder = f'{placeholders[field]} *' if self.fields[field].required else placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False

        # Prefill 'full_name' if available in user profile
        if user_profile and user_profile.name:
            self.fields['full_name'].initial = user_profile.name

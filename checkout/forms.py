from django import forms
from .models import Order
from django.core.exceptions import ValidationError


class OrderForm(forms.ModelForm):
    """A form for capturing order details."""

    full_name = forms.CharField(max_length=50)
    postcode = forms.CharField(max_length=20, required=True)

    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)

        # Set initial values for 'full_name' if user profile is provided
        if user_profile and hasattr(user_profile, 'name'):
            self.initial['full_name'] = user_profile.name

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

        for field in self.fields:
            if field != 'country':  # Country field does not get a placeholder
                placeholder = placeholders[field]
                if self.fields[field].required:
                    placeholder = f'{placeholder} *'
                self.fields[field].widget.attrs['placeholder'] = placeholder

            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False  # Optionally remove labels

    def clean_postcode(self):
        """Custom validation for the postcode field."""
        postcode = self.cleaned_data.get('postcode')
        if len(postcode) < 5:
            raise ValidationError("Postcode is too short.")
        return postcode

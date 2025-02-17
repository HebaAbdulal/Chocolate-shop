from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'name',
            'default_phone_number',
            'default_postcode',
            'default_town_or_city',
            'default_street_address1',
            'default_street_address2',
            'default_county'
        )

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels, and set autofocus on the first field.
        """
        super().__init__(*args, **kwargs)

        # Placeholder definitions
        placeholders = {
            'name': 'Full Name',
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State, or Locality',
        }

        # Autofocus on the first field
        self.fields['name'].widget.attrs['autofocus'] = True

        for field in self.fields:
            if field != 'default_country':
                placeholder = placeholders.get(field, '')
                if self.fields[field].required:
                    placeholder += ' *'  # Mark required fields
                self.fields[field].widget.attrs.update({
                    'placeholder': placeholder,
                    'class': 'border-brown rounded-0 profile-form-input',
                })
            # Hide labels
            self.fields[field].label = False

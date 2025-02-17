from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category, Review


class CustomClearableFileInput(forms.ClearableFileInput):
    input_text = "Choose a file"
    clear_checkbox_label = "Remove file"
    initial_text = "Currently"
    checkbox_name = None
    checkbox_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'id': 'new-image'})


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(
        label='Image', required=False, widget=CustomClearableFileInput
    )
    description = forms.CharField(
        required=False, widget=forms.Textarea, label="Description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        # Use the `friendly_name` attribute directly
        friendly_names = [(c.id, c.friendly_name) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'


class AddToWishlistForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
        }

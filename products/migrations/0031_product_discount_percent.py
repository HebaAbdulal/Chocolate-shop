# Generated by Django 5.1.2 on 2024-12-03 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount_percent',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Discount percentage (e.g., 10 for 10%)', max_digits=5),
        ),
    ]

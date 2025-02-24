# Generated by Django 5.1.2 on 2024-11-26 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_rename_comment_review_review_text_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='review',
            name='review_text',
            field=models.TextField(default='No review provided yet.'),
        ),
    ]

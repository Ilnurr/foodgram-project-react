# Generated by Django 3.2.16 on 2023-06-16 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_subscribed'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Subscribed',
        ),
    ]
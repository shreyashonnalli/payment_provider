# Generated by Django 4.2 on 2023-04-10 20:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paymentapp', '0009_alter_checkout_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkout',
            name='type',
        ),
    ]
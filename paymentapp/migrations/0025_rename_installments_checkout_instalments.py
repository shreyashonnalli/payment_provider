# Generated by Django 4.2 on 2023-05-10 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paymentapp', '0024_alter_transaction_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='checkout',
            old_name='installments',
            new_name='instalments',
        ),
    ]

# Generated by Django 4.2 on 2023-04-10 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paymentapp', '0007_checkout_currency_checkout_merchant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchant',
            name='API_KEY',
            field=models.CharField(max_length=50),
        ),
    ]

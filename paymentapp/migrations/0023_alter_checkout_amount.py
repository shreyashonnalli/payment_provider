# Generated by Django 4.2 on 2023-05-09 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paymentapp', '0022_alter_checkout_cvv_alter_checkout_exp_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkout',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
# Generated by Django 4.2 on 2023-04-06 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paymentapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currency',
            name='id',
        ),
        migrations.AlterField(
            model_name='currency',
            name='code',
            field=models.CharField(max_length=3, primary_key=True, serialize=False),
        ),
    ]

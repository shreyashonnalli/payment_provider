from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Currency(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=30)


class Merchant(models.Model):
    name = models.CharField(max_length=100)
    API_KEY = models.CharField(max_length=50)


class Transaction(models.Model):
    date = models.DateTimeField(null=True)
    status = models.CharField(max_length=15, null=True)
    amount = models.IntegerField()
    checkouts = models.ManyToManyField("Checkout")


class Checkout(models.Model):
    # FK
    _merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    merchant = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        self.merchant = self._merchant.name
        super().save(*args, **kwargs)

    amount = models.IntegerField()
    # FK
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    status = models.CharField(max_length=15)
    date = models.DateTimeField(auto_now_add=True)
    number = models.IntegerField(
        validators=[
            MinValueValidator(1000000000000000),
            MaxValueValidator(9999999999999999),
        ],
        null=True,
    )
    exp_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], null=True
    )
    exp_year = models.IntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(9999)], null=True
    )
    name = models.CharField(max_length=20, null=True)
    cvv = models.IntegerField(
        validators=[MinValueValidator(100), MaxValueValidator(999)], null=True
    )
    # FK
    transactions = models.ManyToManyField(Transaction, null=True)
    installments = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    type = models.CharField(max_length=4, default="BNPL")

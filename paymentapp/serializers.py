from rest_framework import serializers
from paymentapp.models import Currency, Merchant, Transaction, Checkout
from datetime import datetime
from decimal import Decimal


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = "__all__"


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Transaction
        exclude = ("checkouts",)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["date"] = (representation["date"])[:-1]
        representation["amount"] = Decimal(representation["amount"])
        return representation


class CheckoutSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    date = serializers.DateTimeField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Checkout
        fields = "__all__"

    """
    def get_iso_date(self, obj):
        if isinstance(obj, datetime):
            print(obj)
            return obj.isoformat()
        return obj
    """

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["transactions"] = TransactionSerializer(
            instance.transactions.all(), many=True
        ).data
        representation["date"] = (representation["date"])[:-1]
        representation["amount"] = Decimal(representation["amount"])
        return representation

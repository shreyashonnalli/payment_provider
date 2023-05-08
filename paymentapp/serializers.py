from rest_framework import serializers
from paymentapp.models import Currency, Merchant, Transaction, Checkout


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = "__all__"


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ("checkouts",)


class CheckoutSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Checkout
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["transactions"] = TransactionSerializer(
            instance.transactions.all(), many=True
        ).data
        return representation

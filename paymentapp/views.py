from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
    HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    HTTP_201_CREATED,
)
from paymentapp.models import Merchant, Currency, Transaction, Checkout
from .serializers import (
    MerchantSerializer,
    CurrencySerializer,
    TransactionSerializer,
    CheckoutSerializer,
)
import json
from datetime import datetime, timedelta
from . import validators
from django.db.models import Q
import random


# Create your views here.

# creates a checkout object and transaction object associated with checkout object, stores in db and returns checkout object


@api_view(["POST"])
def create_checkout(request):
    # check if API_KEY is valid
    if not validators.API_KEY_validator(request.headers):
        return Response(
            {"error": "No API_KEY provided or key is invalid."},
            status=HTTP_401_UNAUTHORIZED,
        )

    # check if body has appropriate info
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError as e:
        return Response(
            {
                "error": "error while parsing request body. Make sure you're sending json in body"
            },
            status=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )
    if not validators.create_checkout_validator(body):
        return Response(
            {
                "error": "Invalid details in body. Make sure you have amount, description and currency. Make sure currency is a string with max three letters and all caps. Make sure description is not empty(string). Make sure amount is a decimal > 0."
            },
            status=HTTP_400_BAD_REQUEST,
        )

    # get appropriate info from body and create new transaction and checkout object associated to it. Add to db.
    currency_db = Currency.objects.filter(code=body["currency"]).first()
    merchant_db = Merchant.objects.filter(
        API_KEY=validators.get_token(request.headers)
    ).first()

    new_checkout = Checkout(
        _merchant=merchant_db,
        amount=body["amount"],
        currency=currency_db,
        description=body["description"],
        status="PENDING",
        instalments=1,
    )
    new_checkout.save()

    # Return the checkout object
    checkout_serializer = CheckoutSerializer(new_checkout)
    return Response(checkout_serializer.data, status=HTTP_201_CREATED)


# Given an checkout_id, and updated checkout object, we start the process of transaction if card details are valid
@api_view(["POST"])
def initiate_transaction(request, checkout_id):
    if not validators.API_KEY_validator(request.headers):
        return Response(
            {"error": "No API_KEY provided or key is invalid."},
            status=HTTP_401_UNAUTHORIZED,
        )

    merchant_db = Merchant.objects.filter(
        API_KEY=validators.get_token(request.headers)
    ).first()
    checkout = Checkout.objects.filter(id=checkout_id).first()

    # Make sure this checkout is accessible by the merchant requesting
    if not validators.checkout_valid(checkout, merchant_db):
        return Response(
            {"error": "Checkout doesn't exist or not valid for this merchant."},
            status=HTTP_401_UNAUTHORIZED,
        )
    if checkout.status != "PENDING":
        return Response(
            {"error": "Transaction already completed for this checkout!"},
            status=HTTP_400_BAD_REQUEST,
        )

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError as e:
        return Response(
            {
                "error": "error while parsing request body. Make sure you're sending media type application/json in body"
            },
            status=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    if (
        not "name" in body
        or not "number" in body
        or not "exp_month" in body
        or not "exp_year" in body
        or not "cvv" in body
    ):
        return Response(
            {"error": "Need fields name, number, exp_month, exp_year and cvv"},
            status=HTTP_400_BAD_REQUEST,
        )

    name = body["name"]
    number = body["number"]
    exp_month = body["exp_month"]
    exp_year = body["exp_year"]
    cvv = body["cvv"]
    if not validators.card_validator(name, number, exp_month, exp_year, cvv):
        checkout.status = "FAILED"
        checkout.save()
        checkout_serializer = CheckoutSerializer(checkout)
        return Response(checkout_serializer.data, status=HTTP_400_BAD_REQUEST)

    checkout.name = name
    checkout.number = number
    checkout.exp_month = exp_month
    checkout.exp_year = exp_year
    checkout.cvv = cvv
    checkout.status = "INPROGRESS"

    new_transaction = Transaction(
        amount=checkout.amount, date=datetime.now() + timedelta(days=7)
    )
    new_transaction.save()

    new_transaction.checkouts.set([checkout])
    checkout.transactions.add(new_transaction)

    new_transaction.save()
    checkout.save()
    checkout_serializer = CheckoutSerializer(checkout)
    return Response(checkout_serializer.data, status=HTTP_200_OK)


# returns a checkout object of a given checkout id to view
@api_view(["GET"])
def get_checkout(request, checkout_id):
    if not validators.API_KEY_validator(request.headers):
        return Response(
            {"error": "No API_KEY provided or key is invalid."},
            status=HTTP_401_UNAUTHORIZED,
        )

    merchant_db = Merchant.objects.filter(
        API_KEY=validators.get_token(request.headers)
    ).first()
    checkout = Checkout.objects.filter(id=checkout_id).first()

    # Make sure this checkout is accessible by the merchant requesting
    if not validators.checkout_valid(checkout, merchant_db):
        return Response(
            {"error": "Checkout doesn't exist or not valid for this merchant."},
            status=HTTP_401_UNAUTHORIZED,
        )

    # return checkout object
    checkout_serializer = CheckoutSerializer(checkout)
    return Response(checkout_serializer.data, status=HTTP_200_OK)


# returns status of a checkout object, no need for api key
@api_view(["GET"])
def get_status(request, checkout_id):
    checkout = Checkout.objects.filter(id=checkout_id).first()
    if checkout is None:
        return Response(
            {"error": "No checkout found for this ID."}, status=HTTP_400_BAD_REQUEST
        )

    return Response(
        {
            "status": checkout.status,
            "amount": checkout.amount,
            "currency": checkout.currency.code,
        },
        status=HTTP_200_OK,
    )


# Cancels a checkout object if its still pending, otherwise cannot cancel


@api_view(["DELETE"])
def cancel_checkout(request, checkout_id):
    if not validators.API_KEY_validator(request.headers):
        return Response(
            {"error": "No API_KEY provided or key is invalid."},
            status=HTTP_401_UNAUTHORIZED,
        )

    merchant_db = Merchant.objects.filter(
        API_KEY=validators.get_token(request.headers)
    ).first()
    checkout = Checkout.objects.filter(id=checkout_id).first()

    # Make sure this checkout is accessible by the merchant requesting
    if not validators.checkout_valid(checkout, merchant_db):
        return Response(
            {"error": "Checkout doesn't exist or not valid for this merchant."},
            status=HTTP_401_UNAUTHORIZED,
        )

    if checkout.status != "PENDING":
        return Response(
            {
                "error": "Transaction has already been initiated/complete for this checkout. Cannot cancel"
            },
            status=HTTP_400_BAD_REQUEST,
        )

    transactions_with_checkout = checkout.transactions.all()
    if transactions_with_checkout.count() > 0:
        transactions_with_checkout[0].delete()
    checkout.delete()

    return Response(
        {"message": "Checkout object successfully deleted!"}, status=HTTP_200_OK
    )


# Refunding a checkout is only possible if payment has already happened i.e. customer has already paid the money. Otherwise not possible
# Given checkout_id and api authentication key, this endpoint will refund the payment to the customer if already successful


@api_view(["POST"])
def refund_checkout(request, checkout_id):
    if not validators.API_KEY_validator(request.headers):
        return Response(
            {"error": "No API_KEY provided or key does not exist."},
            status=HTTP_401_UNAUTHORIZED,
        )

    merchant_db = Merchant.objects.filter(
        API_KEY=validators.get_token(request.headers)
    ).first()
    checkout = Checkout.objects.filter(id=checkout_id).first()

    # Make sure this checkout is accessible by the merchant requesting
    if not validators.checkout_valid(checkout, merchant_db):
        return Response(
            {"error": "Checkout doesn't exist or not valid for this merchant."},
            status=HTTP_401_UNAUTHORIZED,
        )

    if checkout.status != "SUCCESSFUL":
        if checkout.status == "INPROGRESS":
            return Response(
                {
                    "error": "Payments are yet to be taken from your account. You can only refund after that date"
                },
                status=HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {
                    "error": "Not possible to refund this checkout as it is still PENDING, FAILED, DECLINED OR DEBT"
                },
                status=HTTP_400_BAD_REQUEST,
            )

    transaction_in_checkout = checkout.transactions.all()[0]
    checkout.status = "REFUNDED"
    transaction_in_checkout.status = "REFUNDED"
    checkout.save()
    transaction_in_checkout.save()

    checkout_serializer = CheckoutSerializer(checkout)
    return Response(checkout_serializer.data, status=HTTP_200_OK)


# This endpoint is called to begin transferring of funds of all checkouts in the Buy Now Pay Later Scheme. It is triggered by an external script calling this endpoint once every day.


def bernoulli():
    if random.random() < 0.05:
        return 1
    else:
        return 0


@api_view(["PUT"])
def process_transaction(request):
    if (
        not "API-KEY" in request.headers
        or request.headers["API-KEY"] != "a very secret secret"
    ):
        return Response(
            {
                "error": "This is an endpoint for internal calls only. You will be reported to the authorities for unauthorized access attempts"
            },
            status=HTTP_401_UNAUTHORIZED,
        )

    checkouts = Checkout.objects.filter(
        Q(status="INPROGRESS") & Q(transactions__date__lte=datetime.now())
    )
    if len(checkouts) == 0:
        return Response(
            {"message": "No checkouts to trigger money transfers on this day."},
            status=HTTP_200_OK,
        )

    for checkout in checkouts:
        transaction_in_checkout = checkout.transactions.all()[0]
        if bernoulli():
            checkout.status = "DEBT"
            transaction_in_checkout.status = "DECLINED"
        else:
            checkout.status = "SUCCESSFUL"
            transaction_in_checkout.status = "SUCCESSFUL"
        checkout.save()
        transaction_in_checkout.save()

    return Response(
        {"message": "All checkouts have been successfully processed!"},
        status=HTTP_200_OK,
    )

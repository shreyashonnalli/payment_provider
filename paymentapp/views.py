from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from paymentapp.models import Merchant, Currency, Transaction, Checkout
from django.core import serializers
from django.http import JsonResponse
from .serializers import MerchantSerializer, CurrencySerializer, TransactionSerializer, CheckoutSerializer
import json
from datetime import datetime, timedelta
from . import validators

# Create your views here.

# creates a checkout object and transaction object associated with checkout object, stores in db and returns checkout object


@api_view(['POST'])
def create_checkout(request):
    if not 'API-KEY' in request.headers:
        return Response({'error': 'no API-KEY provided in header'})
    API_KEY = request.headers['API-KEY']
    merchant_db = Merchant.objects.filter(API_KEY=API_KEY).first()
    if merchant_db is None:
        return Response({'error': 'Not an authorised merchant for this Payment Service!'})

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError as e:
        return Response({'error': 'error while parsing request body. Make sure you\'re sending json in body'})
    if not 'amount' in body or not 'currency' in body or not 'description' in body:
        return Response({'error': 'not appropriate keys in body. Need keys amount, description and currency'})
    if not isinstance(body['amount'], int) or not isinstance(body['currency'], str) or not isinstance(body['description'], str):
        return Response({'error': 'amount needs to be an integer, currency needs to be a a string, description needs to be a string'})
    if len(body['currency']) > 3 or len(body['description']) == 0:
        return Response({'error': 'currency needs to be of max length 3 letters (ALL CAPS), description must include something'})
    if (body['amount'] < 1):
        return Response({'error': 'invalid amount entered'})

    currency_code = body['currency']
    currency_db = Currency.objects.filter(code=currency_code).first()
    if currency_db is None:
        return Response({'error': 'currency code doesnt exist. For list of available currencies we accept, Visit https://developers.google.com/adsense/management/appendix/currencies'})
    amount = body['amount']

    new_checkout = Checkout(merchant=merchant_db,
                            amount=amount, currency=currency_db, description=body['description'], status='PENDING', installments=1)
    new_transaction = Transaction(status='PENDING', amount=amount)

    new_transaction.save()
    new_checkout.save()

    new_transaction.checkouts.set([new_checkout])
    new_checkout.transactions.add(new_transaction)

    new_transaction.save()
    new_checkout.save()

    checkout_serializer = CheckoutSerializer(new_checkout)
    return Response(checkout_serializer.data)


# Given an checkout_id, and updated checkout object, we start the process of transaction if card details are valid
@api_view(['POST'])
def initiate_transaction(request, checkout_id):
    if not 'API-KEY' in request.headers:
        return Response({'error': 'no API-KEY provided in header'})
    API_KEY = request.headers['API-KEY']
    merchant_db = Merchant.objects.filter(API_KEY=API_KEY).first()
    if merchant_db is None:
        return Response({'error': 'Not an authorised merchant for this Payment Service!'})

    checkout = Checkout.objects.filter(id=checkout_id).first()
    if checkout is None:
        return Response({'error': 'No checkout found for this ID.'})

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError as e:
        return Response({'error': 'error while parsing request body. Make sure you\'re sending json in body'})

    if not 'name' in body or not 'number' in body or not 'exp_month' in body or not 'exp_year' in body or not 'cvv' in body:
        return Response({'error': 'Need fields name, number, exp_month, exp_year and cvv'})
    name = body['name']
    number = body['number']
    exp_month = body['exp_month']
    exp_year = body['exp_year']
    cvv = body['cvv']
    if not isinstance(name, str) or not isinstance(number, int) or not isinstance(exp_month, int) or not isinstance(exp_year, int) or not isinstance(cvv, int):
        return Response({'error': 'Inappropriate datatypes. Make sure only name is string and rest are integers'})
    if number < 1000000000000000 or number > 9999999999999999:
        return Response({'error': 'Number not 16 digits'})
    if exp_month < 1 or exp_month > 12:
        return Response({'error': 'Invalid exp_month'})
    if exp_year < 2023 or exp_year > 9999:
        return Response({'error': 'Invalid exp_year or card expired'})
    if cvv < 100 or cvv > 999:
        return Response({'error': 'Invalid CVV'})
    if name == "":
        return Response({'error': 'Empty Name'})
    if validators.is_month_year_in_past(exp_month, exp_year):
        return Response({'error': 'Card Expired!'})

    checkout.name = name
    checkout.number = number
    checkout.exp_month = exp_month
    checkout.exp_year = exp_year
    checkout.cvv = cvv
    checkout.status = "INPROGRESS"
    transaction_in_checkout = checkout.transactions.all()[0]
    transaction_in_checkout.date = datetime.now() + timedelta(days=7)
    transaction_in_checkout.status = "INPROGRESS"

    checkout.save()
    transaction_in_checkout.save()

    checkout_serializer = CheckoutSerializer(checkout)
    return Response(checkout_serializer.data)

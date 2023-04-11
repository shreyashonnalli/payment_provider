from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from paymentapp.models import Merchant, Currency, Transaction, Checkout
from django.core import serializers
from django.http import JsonResponse
from .serializers import MerchantSerializer, CurrencySerializer, TransactionSerializer, CheckoutSerializer
import json
from datetime import datetime, timedelta


# Create your views here.
@api_view(['POST'])
def create_checkout(request):
    if not 'API-KEY' in request.headers:
        return Response({'error': 'no API-KEY provided in header'})
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

    API_KEY = request.headers['API-KEY']
    merchant_db = Merchant.objects.filter(API_KEY=API_KEY).first()
    if merchant_db is None:
        return Response({'error': 'Not an authorised merchant for this Payment Service!'})
    currency_code = body['currency']
    currency_db = Currency.objects.filter(code=currency_code).first()
    if currency_db is None:
        return Response({'error': 'currency code doesnt exist. For list of available currencies we accept, Visit https://developers.google.com/adsense/management/appendix/currencies'})
    amount = body['amount']

    new_checkout = Checkout(merchant=merchant_db,
                            amount=amount, currency=currency_db, description=body['description'], status='PENDING', installments=1)
    new_transaction = Transaction(
        date=datetime.now() + timedelta(days=7), status='PENDING', amount=amount)

    new_transaction.save()
    new_checkout.save()

    new_transaction.checkouts.set([new_checkout])
    new_checkout.transactions.add(new_transaction)

    new_transaction.save()
    new_checkout.save()

    checkout_serializer = CheckoutSerializer(new_checkout)
    return Response(checkout_serializer.data)

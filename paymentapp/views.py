from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from paymentapp.models import Merchant, Currency, Transaction, Checkout
from django.core import serializers
from django.http import JsonResponse
from .serializers import MerchantSerializer
import json


# Create your views here.
@api_view(['POST'])
def create_checkout(request):
    if not 'API-KEY' in request.headers:
        return Response({'error': 'no API-KEY provided in header'})
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError as e:
        return Response({'error': 'error while parsing request body. Make sure you\'re sending json in body'})
    if not 'amount' in body or not 'currency' in body:
        return Response({'error': 'not appropriate keys in body. Need keys amount and currency'})
    if not isinstance(body['amount'], int) or not isinstance(body['currency'], str):
        return Response({'error': 'amount needs to be an integer, currency needs to be a a string'})
    if len(body['currency']) > 3:
        return Response({'error': 'currency needs to be of max length 3 letters (ALL CAPS)'})
    if (body['amount'] < 1):
        return Response({'error': 'invalid amount entered'})

    API_KEY = request.headers['API-KEY']
    merchant = Merchant.objects.filter(API_KEY=API_KEY).first()
    if merchant is None:
        return Response({'error': 'Not an authorised merchant for this Payment Service!'})
    currency_code = body['currency']
    if not Currency.objects.filter(code=currency_code).exists():
        return Response({'error': 'currency code doesnt exist. For list of available currencies we accept. Visit https://developers.google.com/adsense/management/appendix/currencies'})
    amount = body['amount']

    return Response({'data': 'lol'})

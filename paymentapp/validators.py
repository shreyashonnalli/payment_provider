import datetime
from paymentapp.models import Merchant, Currency, Transaction, Checkout


def is_month_year_in_past(month, year):
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    if year < current_year:
        return True
    elif year == current_year:
        if month < current_month:
            return True

    return False


def card_validator(name, number, exp_month, exp_year, cvv):
    if not isinstance(name, str) or not isinstance(number, int) or not isinstance(exp_month, int) or not isinstance(exp_year, int) or not isinstance(cvv, int):
        return 0
    if number < 1000000000000000 or number > 9999999999999999:
        return 0
    if exp_month < 1 or exp_month > 12:
        return 0
    if exp_year < 2023 or exp_year > 9999:
        return 0
    if cvv < 100 or cvv > 999:
        return 0
    if name == "":
        return 0
    if is_month_year_in_past(exp_month, exp_year):
        return 0
    return 1


def create_checkout_validator(body):
    if not 'amount' in body or not 'currency' in body or not 'description' in body:
        return 0
    if not isinstance(body['amount'], int) or not isinstance(body['currency'], str) or not isinstance(body['description'], str):
        return 0
    if len(body['currency']) > 3 or len(body['description']) == 0:
        return 0
    if (body['amount'] < 1):
        return 0
    currency_code = body['currency']
    currency_db = Currency.objects.filter(code=currency_code).first()
    if currency_db is None:
        return 0
    return 1


def API_KEY_validator(headers):
    if not 'API-KEY' in headers:
        return 0
    API_KEY = headers['API-KEY']
    merchant_db = Merchant.objects.filter(API_KEY=API_KEY).first()
    if merchant_db is None:
        return 0
    return 1


def checkout_valid(checkout, merchant):
    if checkout is None:
        return 0
    if merchant.id != checkout.merchant.id:
        return 0
    return 1

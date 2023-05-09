import datetime
from paymentapp.models import Merchant, Currency, Transaction, Checkout


def is_month_year_in_past(month, year):
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    if year < 23:
        return True
    elif year == 23:
        if month <= current_month:
            return True

    return False


def card_validator(name, number, exp_month, exp_year, cvv):
    if (
        not isinstance(name, str)
        or not isinstance(number, int)
        or not isinstance(exp_month, int)
        or not isinstance(exp_year, int)
        or not isinstance(cvv, int)
    ):
        return 0
    if number < 1000000000000000 or number > 9999999999999999:
        print("fail 1")
        return 0
    if exp_month < 1 or exp_month > 12:
        print("fail 2")
        return 0
    if exp_year < 0 or exp_year > 99:
        print("fail 3")
        return 0
    if cvv < 100 or cvv > 9999:
        print("fail 4")
        return 0
    if name == "":
        print("fail 5")
        return 0
    if is_month_year_in_past(exp_month, exp_year):
        print("fail 6")
        return 0
    return 1


def create_checkout_validator(body):
    if not "amount" in body or not "currency" in body or not "description" in body:
        return 0
    if (
        not isinstance(body["amount"], int)
        or not isinstance(body["currency"], str)
        or not isinstance(body["description"], str)
    ):
        return 0
    if len(body["currency"]) > 3 or len(body["description"]) == 0:
        return 0
    if body["amount"] < 1:
        return 0
    currency_code = body["currency"]
    currency_db = Currency.objects.filter(code=currency_code).first()
    if currency_db is None:
        return 0
    return 1


def get_token(headers):
    auth_header = headers["Authorization"]
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        return token


def API_KEY_validator(headers):
    if not "Authorization" in headers:
        return 0
    token = get_token(headers)
    merchant_db = Merchant.objects.filter(API_KEY=token).first()
    if merchant_db is None:
        return 0
    return 1


def checkout_valid(checkout, merchant):
    if checkout is None:
        return 0
    if merchant.id != checkout._merchant.id:
        return 0
    return 1

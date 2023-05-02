import requests
import schedule
import time

url = 'http://127.0.0.1:8000/api/checkout/process'
headers = {'API-KEY': 'a very secret secret'}


def process_checkout():
    response = requests.put(url, headers=headers)
    print(f"HTTP POST response: {response.status_code}")
    print(response.json())


process_checkout()

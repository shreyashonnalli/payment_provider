import requests
url = 'http://sc20sh.pythonanywhere.com/api/checkout/process'
headers = {'API-KEY': 'a very secret secret'}


def process_checkout():
    response = requests.put(url, headers=headers)
    print(f"HTTP POST response: {response.status_code}")
    print(response.json())


process_checkout()

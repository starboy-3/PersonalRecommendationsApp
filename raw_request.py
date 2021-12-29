import requests

response = requests.request(method="GET", url="https://market.yandex.ru", timeout=5).content.decode("utf-8")

print(response)
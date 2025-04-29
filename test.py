from requests import get, post, put, delete

# Testing new user apis
BASE_URL = "http://127.0.0.1:5000/api"


# Test posting new user
response = post(f"{BASE_URL}/users", json={
    "email": "Ivan2009e@yandex.ru",
    "verify_code": "63948642830128870114753",
    "password": "Ivan2009e",
    "name": "Ivan Ivanov",
})
print(response.json())


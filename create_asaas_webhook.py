import os
import requests

is_local = os.path.exists('.env')

if is_local:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env

if __name__ == "__main__":
    ASAAS_BASE_URL_PROD = "https://api.asaas.com/v3"
    ASAAS_API_KEY_PROD = os.environ.get("ASAAS_API_KEY_PROD")
    API_PROD_URL = os.environ.get("API_PROD_URL")
    url = f"{ASAAS_BASE_URL_PROD}/webhooks"

    payload = {
        "name": "Payment Status Webook",
        "url": f"{API_PROD_URL}/webhook-asaas",
        "email": "nicholasyukio@gmail.com",
        "enabled": True,
        "interrupted": False,
        "apiVersion": 3,
        "authToken": "5tLxsL6uoN",
        "sendType": "SEQUENTIALLY",
        "events": ["PAYMENT_CREATED", "PAYMENT_AUTHORIZED", "PAYMENT_UPDATED", "PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": ASAAS_API_KEY_PROD
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
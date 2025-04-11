from flask import Flask, jsonify, request
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

#ASAAS_API_KEY = os.environ.get("ASAAS_API_KEY")
ASAAS_BASE_URL = "https://api-sandbox.asaas.com/v3"


@app.route("/")
def home():
    return jsonify({"message": "API is running"})


@app.route("/create-pix-charge", methods=["POST"])
def create_pix_charge():
    # Get client data from request
    data = request.json
    name = data.get("name")
    cpf_cnpj = data.get("cpfCnpj")
    email = data.get("email")
    value = data.get("value")

    # Create or get customer
    customer_id = create_or_get_customer(name, cpf_cnpj, email)
    if not customer_id:
        return jsonify({"error": "Failed to create or retrieve customer"}), 500

    # Create PIX charge
    charge_response = create_pix_payment(customer_id, value)
    if not charge_response:
        return jsonify({"error": "Failed to create PIX charge"}), 500

    return jsonify(charge_response)


def create_or_get_customer(name, cpf_cnpj, email):
    # Check if customer already exists
    headers = {"access_token": ASAAS_API_KEY}
    response = requests.get(
        f"{ASAAS_BASE_URL}/customers",
        params={"cpfCnpj": cpf_cnpj},
        headers=headers
    )

    if response.status_code == 200 and response.json().get("data"):
        return response.json()["data"][0]["id"]

    # If not, create a new customer
    payload = {
        "name": name,
        "cpfCnpj": cpf_cnpj,
        "email": email
    }

    response = requests.post(
        f"{ASAAS_BASE_URL}/customers",
        json=payload,
        headers=headers
    )

    print(response.json())
    if response.status_code == 200:
        return response.json()["id"]
    return None


def create_pix_payment(customer_id, value):
    url = "https://api-sandbox.asaas.com/v3/pix/qrCodes/static"

    # You can get this from your Asaas account
    access_token = ASAAS_API_KEY
    address_key = "44282205000182"  # Pix key registered at Asaas

    # Generate expiration date (e.g., 30 minutes from now)
    expiration_date = (datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "addressKey": address_key,
        "description": "Checkout payment",
        "value": value,
        "format": "ALL",
        "expirationDate": expiration_date,
        "expirationSeconds": None,
        "allowsMultiplePayments": True,
        "externalReference": customer_id
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": access_token
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error creating PIX charge:", response.text)
        return None


if __name__ == "__main__":
    app.run(debug=True)

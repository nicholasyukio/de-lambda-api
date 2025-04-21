from flask import Flask, jsonify, request
import requests
import os
from datetime import datetime, timedelta
from flask_cors import CORS

is_local = os.path.exists('.env')

if is_local:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env

app = Flask(__name__)

allowed_origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://dominioeletrico.com.br",
]

CORS(app, origins=allowed_origins)

ASAAS_API_KEY = os.environ.get("ASAAS_API_KEY")
ASAAS_API_KEY_PROD = os.environ.get("ASAAS_API_KEY_PROD")
GREETING = os.environ.get("GREETING")
ASAAS_BASE_URL = "https://api-sandbox.asaas.com/v3"
ASAAS_BASE_URL_PROD = "https://api.asaas.com/v3"


@app.route("/")
def home():
    return jsonify({"message": "API is running !!## "+GREETING})

@app.route("/debug")
def debug():
    return jsonify({
        "GREETING": GREETING
    })

@app.route("/create-pix-charge", methods=["POST"])
def create_pix_charge():
    # Get client data from request
    data = request.json
    name = data.get("name")
    cpf_cnpj = data.get("cpfCnpj")
    email = data.get("email")
    phone = data.get("phone")
    value = data.get("value")

    # Create or get customer
    customer_id = create_or_get_customer_for_pix(name, cpf_cnpj, email, phone)
    if not customer_id:
        return jsonify({"error": "Failed to create or retrieve customer"}), 500

    # Create PIX charge
    charge_response = create_pix_payment(customer_id, value)
    if not charge_response:
        return jsonify({"error": "Failed to create PIX charge"}), 500

    return jsonify(charge_response)

@app.route("/create-card-charge", methods=["POST"])
def create_card_charge():
    # Get client data from request
    data = request.json
    name = data.get("name")
    cpf_cnpj = data.get("cpfCnpj")
    email = data.get("email")
    phone = data.get("phone")
    value = data.get("value")
    n_inst = data.get("n_inst")
    inst_value = data.get("inst_value")
    customer_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Address data
    cep = data.get("cep")
    address = data.get("address")
    province = data.get("province")
    addressNumber = data.get("addressNumber")
    addressComplement = data.get("addressComplement")

    # Credit card data
    holderName = data.get("holderName")
    cardNumber = data.get("cardNumber")
    expiryMonth = data.get("expiryMonth")
    expiryYear = data.get("expiryYear")
    cvv = data.get("cvv")

    # Create or get customer
    customer_id = create_or_get_customer(name, cpf_cnpj, email, phone, address, addressNumber, addressComplement, province, cep)
    if not customer_id:
        return jsonify({"error": "Failed to create or retrieve customer"}), 500
    
    creditCard = {
        "holderName": holderName,
        "number": cardNumber,
        "expiryMonth": str(expiryMonth),
        "expiryYear": str(expiryYear),
        "ccv": cvv
    }
    creditCardHolderInfo = {
        "name": name,
        "email": email,
        "cpfCnpj": cpf_cnpj,
        "postalCode": cep,
        "addressNumber": addressNumber,
        "addressComplement": addressComplement,
        "phone": phone,
        "mobilePhone": phone
    }

    # Create CREDIT CARD charge
    charge_response = create_credit_card_payment(customer_id, value, n_inst, inst_value, creditCard, creditCardHolderInfo, customer_ip)
    if not charge_response:
        return jsonify({"error": "Failed to create CREDIT CARD charge"}), 500

    return jsonify(charge_response)

@app.route("/verify-payment/<id>")
def verify_payment(id):
    if not id:
        return {"error": "Missing payment ID"}, 400
    headers = {"accept": "application/json", "access_token": ASAAS_API_KEY_PROD}
    response = requests.get(
        f"{ASAAS_BASE_URL_PROD}/payments/{id}/status",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print("Error verifying payment", response.text)
        print("Status code: ", response.status_code)
        return {"error": "Failed to verify payment"}
    
@app.route("/webhook-asaas", methods=["POST"])
def webhook_asaas():
    data = request.json
    print("Received webhook: ", data)
    event_type = data.get("event")
    payment = data.get("payment", {})
    payment_id = payment.get("id")
    status = payment.get("status")
    external_reference = payment.get("externalReference")
    return jsonify({"received": True}), 200


def create_or_get_customer_for_pix(name, cpf_cnpj, email, phone):
    # Check if customer already exists
    headers = {"access_token": ASAAS_API_KEY_PROD}
    response = requests.get(
        f"{ASAAS_BASE_URL_PROD}/customers",
        params={"cpfCnpj": cpf_cnpj},
        headers=headers
    )

    if response.status_code == 200 and response.json().get("data"):
        return response.json()["data"][0]["id"]

    # If not, create a new customer
    payload = {
        "name": name,
        "cpfCnpj": cpf_cnpj,
        "email": email,
        "phone": phone,
        "mobilePhone": phone
    }

    response = requests.post(
        f"{ASAAS_BASE_URL_PROD}/customers",
        json=payload,
        headers=headers
    )

    print(response.json())
    if response.status_code == 200:
        return response.json()["id"]
    return None

def create_or_get_customer(name, cpf_cnpj, email, phone, address, addressNumber, complement, province, postalCode):
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
        "email": email,
        "phone": phone,
        "mobilePhone": phone,
        "address": address,
        "addressNumber": addressNumber,
        "complement": complement,
        "province": province,
        "postalCode": postalCode
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
    url = f"{ASAAS_BASE_URL_PROD}/pix/qrCodes/static"

    # You can get this from your Asaas account
    access_token = ASAAS_API_KEY_PROD
    address_key = "8707e564-fcc8-45d5-ad8a-bb49ddc17696"  # Pix key registered at Asaas

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
    
def create_credit_card_payment(customer_id, value, n_inst, inst_value, creditCard, creditCardHolderInfo, customer_ip):
    url = "https://api-sandbox.asaas.com/v3/payments/"
    r = 0.02

    # You can get this from your Asaas account
    access_token = ASAAS_API_KEY

    # Generate expiration date (e.g., 30 minutes from now)
    dueDate = (datetime.now()).strftime("%Y-%m-%d")

    totalValue = n_inst * inst_value

    payload = {
        "billingType": "CREDIT_CARD",
        "value": value,
        "dueDate": dueDate,
        "description": "Curso Domínio Elétrico",
        "customer": customer_id,
        "installmentCount": n_inst,
        "totalValue": totalValue,
        "creditCard": creditCard,
        "creditCardHolderInfo": creditCardHolderInfo,
        "authorizeOnly": False,
        "remoteIp": customer_ip
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
        print("Error creating CARD charge:", response.text)
        return None


if __name__ == "__main__":
    app.run(debug=True)

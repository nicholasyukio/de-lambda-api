from flask import Flask, jsonify, request
import requests
import os
import uuid
import dynamodb
import moodle
import brevo
import random_passwords
import create_course
import bunny
import users
from datetime import datetime, timedelta
from flask_cors import CORS

is_local = os.path.exists('.env')

if is_local:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env
    # In development, uses Sandbox key and base URL for credit card and Prod key and base URL for Pix
    ASAAS_API_KEY = os.environ.get("ASAAS_API_KEY")
    ASAAS_API_KEY_PROD = os.environ.get("ASAAS_API_KEY_PROD")
    ASAAS_BASE_URL = "https://api-sandbox.asaas.com/v3"
    ASAAS_BASE_URL_PROD = "https://api.asaas.com/v3"
else:
    # In production, uses Prod key and base URL for both credit card and Pix
    ASAAS_API_KEY = os.environ.get("ASAAS_API_KEY_PROD")
    ASAAS_API_KEY_PROD = os.environ.get("ASAAS_API_KEY_PROD")
    ASAAS_BASE_URL = "https://api.asaas.com/v3"
    ASAAS_BASE_URL_PROD = "https://api.asaas.com/v3"


app = Flask(__name__)

allowed_origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://dominioeletrico.com.br",
]

CORS(app, origins=allowed_origins)

GREETING = os.environ.get("GREETING")

@app.route("/")
def home():
    return jsonify({"message": "API is running !!## "+GREETING})

@app.route("/debug")
def debug():
    return jsonify({
        "GREETING": GREETING
    })

@app.route('/courses', methods=['GET'])
def get_all_courses():
    courses = create_course.get_all_courses()
    return jsonify(courses)

# API endpoint to get all course content
@app.route('/courses/<string:course_id>', methods=['GET'])
def get_course(course_id):
    courses = create_course.get_course_data(course_id)
    return jsonify(courses)

# API endpoint to get a specific lesson
@app.route('/courses/<string:course_id>/sections/<string:section_id>/lessons/<string:lesson_id>', methods=['GET'])
def get_lesson(course_id, section_id, lesson_id):
    print("teste")
    result = create_course.get_lesson_data(course_id, section_id, lesson_id)
    print(result)
    return jsonify(result)

# API endpoint to get video info from Bunny
@app.route('/videoinfo/<string:video_id>', methods=['GET'])
def videoinfo(video_id):
    print("videoinfo")
    result = bunny.get_video_info(video_id)
    return jsonify(result)


@app.route("/enroll-student", methods=["POST"])
def enroll_student():
    # Get data from the request
    data = request.json
    fullname = data.get("name")
    name_parts = fullname.split()
    first_name = name_parts[0].capitalize()
    email = data.get("email")
    user_id = data.get("user_id")
    payment_method = data.get("payment_method")
    paid_amount = data.get("paid_amount")
    payment_option = data.get("payment_option")
    initial_password = random_passwords.generate()
    workflow_status = {
        "fullname": fullname,
        "email": email,
        "payment_method": payment_method,
        "paid_amount": f"{paid_amount:.2f}",
        "payment_option": payment_option,
        "moodle_response_status": "",
        "brevo_response_status": ""
    }
    workflow_status["moodle_response_status"] = moodle.enroll_student(fullname, email, initial_password)
    workflow_status["brevo_response_status"] = brevo.send_email_to_client(first_name, email, initial_password)
    if user_id:
        users.update_user(user_id, {"account_type": "paid"})
    else:
        pass
        # First implement user creation in AWS Cognito
    brevo.send_email_to_admin(workflow_status)
    return_data = {
        "status": "ok",
        "email": email,
        "password": initial_password
    }
    return jsonify(return_data), 200

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

    print(charge_response["pixid"])
    dynamodb.register_pix_payment(customer_id, charge_response["pixid"], value)
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

@app.route("/verify-payment/<customer_id>")
def verify_payment(customer_id):
    if not customer_id:
        return {"error": "Missing customer_id"}, 400
    result = dynamodb.check_pix_status(customer_id)
    return jsonify({"status": result})
    
@app.route("/webhook-asaas", methods=["POST"])
def webhook_asaas():
    data = request.json
    print("Received webhook: ", data)
    event_type = data.get("event")
    payment = data.get("payment", {})
    customer_id = payment.get("customer")
    status = payment.get("status")
    if event_type == "PAYMENT_RECEIVED":
        dynamodb.confirm_pix_payment(customer_id)
        # Here we put the course enrollment part
    return jsonify({"received": True}), 200

# endpoints for Users

@app.route("/get-user-data/<user_id>")
def get_user_data(user_id):
    if not user_id:
        return {"error": "Missing user_id"}, 400
    result = users.get_user(user_id)
    return jsonify(result)

@app.route("/upgrade-account", methods=["POST"])
def upgrade_account():
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return {"error": "Missing user_id"}, 400
    result = users.update_user(user_id, {"account_type": "paid"})
    return jsonify(result)

@app.route("/enroll-user-in-course", methods=["POST"])
def enroll_user_in_course():
    data = request.get_json()
    user_id = data.get("user_id")
    course_id = data.get("course_id")
    if not user_id or not course_id:
        return {"error": "Missing user_id or course_id"}, 400
    result = users.enroll_user_in_course(user_id, course_id)
    print(result)
    return jsonify(result)

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
        "description": "Curso Domínio Elétrico",
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
        data = response.json()
        data["pixid"] = str(uuid.uuid4())
        data["customer_id"] = customer_id
        return data
    else:
        print("Error creating PIX charge:", response.text)
        return None
    
def create_credit_card_payment(customer_id, value, n_inst, inst_value, creditCard, creditCardHolderInfo, customer_ip):
    url = f"{ASAAS_BASE_URL}/payments"
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

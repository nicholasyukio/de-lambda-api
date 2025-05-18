import requests
import os

is_local = os.path.exists('.env')

if is_local:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env

brevo_api_key = os.getenv("BREVO_API_KEY")
default_password = os.getenv("MOODLE_DE_DEFAULT_PASSWORD")
admin_name = os.getenv("ADMIN_NAME")
admin_email = os.getenv("ADMIN_EMAIL")

def send_email_to_client(first_name, email, password):
    email_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
    }}
    .message {{
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 20px;
        margin: 20px auto;
        max-width: 600px;
        background-color: #f9f9f9;
    }}
    .message h3 {{
        color: #000000;
    }}
    .message p {{
        color: #050505;
    }}
    .link {{
        color: #007bff;
        text-decoration: none;
    }}
    </style>
    </head>
    <body>

    <div class="message">
    <h3>Instruções para acessar o curso Domínio Elétrico</h3>
    <p>Olá, {first_name}!</p>
    <p>Parabéns pela sua inscrição no curso Domínio Elétrico! Isso demonstra um interesse em aprender de verdade circuitos elétricos.</p>
    <p>Ficarei feliz em contribuir com os seus estudos.</p>
    <p>O endereço para você entrar no curso é este:</p>
    <p><a href="https://curso.dominioeletrico.com.br/login/" class="link">https://curso.dominioeletrico.com.br/login/</a></p>
    <p>Você vai entrar com os dados:</p>
    <ul>
        <li><strong>Identificação de usuário:</strong> {email}</li>
        <li><strong>Senha:</strong> {password}</li>
    </ul>
    <p>Sugiro que já salve nos favoritos do navegador.</p>
    <p>Você pode também solicitar a entrada no grupo de alunos no Telegram:</p>
    <p><a href="https://t.me/+ij9lYewIicxhMGYx" class="link">https://t.me/+ij9lYewIicxhMGYx</a> (depois será perguntado pelo Telegram o seu email, para confirmar que você é aluno do curso)</p>
    <p>Aproveito para agradecer e dizer que fico feliz com a confiança depositada no meu trabalho.</p>
    <p>Bons estudos,<br>Nicholas Yukio</p>
    </div>

    </body>
    </html>
    """
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {
            "name": "Nicholas Yukio",
            "email": "noreply@curso.dominioeletrico.com.br"
        },
        "to": [
            {
                "email": email,
                "name": first_name
            }
        ],
        "subject": "[Domínio Elétrico] Dados de acesso ao curso",
        "htmlContent": email_template
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

def send_email_to_admin(workflow_status):
    email_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
    }}
    .message {{
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 20px;
        margin: 20px auto;
        max-width: 600px;
        background-color: #f9f9f9;
    }}
    .message h3 {{
        color: #000000;
    }}
    .message p {{
        color: #050505;
    }}
    .link {{
        color: #007bff;
        text-decoration: none;
    }}
    </style>
    </head>
    <body>

    <div class="message">
    <h3>Nova venda do Domínio Elétrico</h3>
    <h4>Dados da venda:</h4>
    <ul>
        <li><strong>Nome completo:</strong> {workflow_status["fullname"]}</li>
        <li><strong>Email:</strong> {workflow_status["email"]}</li>
        <li><strong>Forma de pagamento:</strong> {workflow_status["payment_method"]}</li>
        <li><strong>Valor pago:</strong> R$ {workflow_status["paid_amount"]}</li>
        <li><strong>Opção de pagamento:</strong> {workflow_status["payment_option"]}</li>
    </ul>
    <h4>Resultados dos cadastros:</h4>
    <ul>
        <li><strong>Moodle:</strong> {workflow_status["moodle_response_status"]}</li>
        <li><strong>Brevo:</strong> {workflow_status["brevo_response_status"]}</li>
    </ul>
    </div>
    </body>
    </html>
    """
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {
            "name": "Nicholas Yukio",
            "email": "noreply@curso.dominioeletrico.com.br"
        },
        "to": [
            {
                "email": admin_email,
                "name": admin_name
            }
        ],
        "subject": "[Domínio Elétrico] NOVA VENDA",
        "htmlContent": email_template
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

def send_notify_email_to_admin(title, message):
    email_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
    }}
    .message {{
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 20px;
        margin: 20px auto;
        max-width: 600px;
        background-color: #f9f9f9;
    }}
    .message h3 {{
        color: #000000;
    }}
    .message p {{
        color: #050505;
    }}
    .link {{
        color: #007bff;
        text-decoration: none;
    }}
    </style>
    </head>
    <body>

    <div class="message">
    <h3>{title}</h3>
    <p><strong>{message}</strong></p>
    </div>
    </body>
    </html>
    """
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {
            "name": "Nicholas Yukio",
            "email": "noreply@curso.dominioeletrico.com.br"
        },
        "to": [
            {
                "email": admin_email,
                "name": admin_name
            }
        ],
        "subject": f"[Domínio Elétrico] {title}",
        "htmlContent": email_template
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

def send_lia_event_email_to_admin(data):
    email_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
    }}
    .message {{
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 20px;
        margin: 20px auto;
        max-width: 600px;
        background-color: #f9f9f9;
    }}
    .message h3 {{
        color: #000000;
    }}
    .message p {{
        color: #050505;
    }}
    .link {{
        color: #007bff;
        text-decoration: none;
    }}
    </style>
    </head>
    <body>

    <div class="message">
    <h3>Lia Event!</h3>
    <h4>Event data:</h4>
    <p>{data}</p>
    </div>
    </body>
    </html>
    """
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {
            "name": "Nicholas Yukio",
            "email": "noreply@curso.dominioeletrico.com.br"
        },
        "to": [
            {
                "email": admin_email,
                "name": admin_name
            }
        ],
        "subject": "[Domínio Elétrico] New Lia Event!",
        "htmlContent": email_template
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

def send_page_events_email_to_admin(data):
    email_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
    }}
    .message {{
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 20px;
        margin: 20px auto;
        max-width: 600px;
        background-color: #f9f9f9;
    }}
    .message h3 {{
        color: #000000;
    }}
    .message p {{
        color: #050505;
    }}
    .link {{
        color: #007bff;
        text-decoration: none;
    }}
    </style>
    </head>
    <body>

    <div class="message">
    <h3>Page events data:</h3>
    <h4>data:</h4>
    {data}
    </div>
    </body>
    </html>
    """
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {
            "name": "Nicholas Yukio",
            "email": "noreply@curso.dominioeletrico.com.br"
        },
        "to": [
            {
                "email": admin_email,
                "name": admin_name
            }
        ],
        "subject": "[Domínio Elétrico] New Page Event Data!",
        "htmlContent": email_template
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

def send_desite_signup_email_to_admin(data):
    email_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
    }}
    .message {{
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 20px;
        margin: 20px auto;
        max-width: 600px;
        background-color: #f9f9f9;
    }}
    .message h3 {{
        color: #000000;
    }}
    .message p {{
        color: #050505;
    }}
    .link {{
        color: #007bff;
        text-decoration: none;
    }}
    </style>
    </head>
    <body>

    <div class="message">
    <h3>New signup in site!</h3>
    <h4>data:</h4>
    {data}
    </div>
    </body>
    </html>
    """
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {
            "name": "Nicholas Yukio",
            "email": "noreply@curso.dominioeletrico.com.br"
        },
        "to": [
            {
                "email": admin_email,
                "name": admin_name
            }
        ],
        "subject": "[Domínio Elétrico] New Signup in Site!",
        "htmlContent": email_template
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

def send_pagarme_email_to_admin(data):
    email_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
    }}
    .message {{
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 20px;
        margin: 20px auto;
        max-width: 600px;
        background-color: #f9f9f9;
    }}
    .message h3 {{
        color: #000000;
    }}
    .message p {{
        color: #050505;
    }}
    .link {{
        color: #007bff;
        text-decoration: none;
    }}
    </style>
    </head>
    <body>

    <div class="message">
    <h3>New Pagarme activity!</h3>
    <h4>data:</h4>
    {data}
    </div>
    </body>
    </html>
    """
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {
            "name": "Nicholas Yukio",
            "email": "noreply@curso.dominioeletrico.com.br"
        },
        "to": [
            {
                "email": admin_email,
                "name": admin_name
            }
        ],
        "subject": "[Domínio Elétrico] New Pagarme activity!",
        "htmlContent": email_template
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

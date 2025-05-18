import boto3
import os

is_local = os.path.exists('.env')

# Load environment variables from .env
if is_local:
    from dotenv import load_dotenv
    load_dotenv()

# Initialize boto3 session with credentials from .env
session = boto3.Session(
    aws_access_key_id=os.getenv("BOTO_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("BOTO_SECRET_ACCESS_KEY"),
    region_name=os.getenv("BOTO_REGION")
)

client = boto3.client('cognito-idp')

def create_user(email, name):
    response = client.admin_create_user(
        UserPoolId=os.getenv("USER_POOL_ID"),
        Username=email,
        UserAttributes=[
            {'Name': 'email', 'Value': email},
            {'Name': 'email_verified', 'Value': 'true'},
            {'Name': 'birthdate', 'Value': '1900-01-01'},
            {'Name': 'gender', 'Value': 'none'},
            {'Name': 'picture', 'Value': 'default_picture_url.png'},
            {'Name': 'phone_number', 'Value': '+1234567890'},
            {'Name': 'given_name', 'Value': name},
            {'Name': 'name', 'Value': name}
        ],
        TemporaryPassword='A-temporary-Pass123!',
        MessageAction='SUPPRESS',  # suppress email from Cognito
    )

    return response

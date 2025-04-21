import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError
from decimal import Decimal

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

# DynamoDB resource
dynamodb = session.resource('dynamodb')

# Table name (change if needed)
TABLE_NAME = "Pix-payments-DE"

# Get table object
table = dynamodb.Table(TABLE_NAME)

def create_table():
    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'customer_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'customer_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Table creation initiated.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Table already exists.")
        else:
            raise

def register_pix_payment(customer_id, pix_id, amount):
    try:
        timestamp = datetime.utcnow().isoformat()
        response = table.get_item(Key={'customer_id': customer_id})
        item_exists = 'Item' in response

        if not item_exists:
            # Cria o item com 'last_payment_id'
            table.put_item(Item={
                'customer_id': customer_id,
                'last_payment_id': pix_id,
                'payments': {
                    pix_id: {
                        'status': 'pending',
                        'amount': Decimal(str(amount)),
                        'timestamp': timestamp
                    }
                }
            })
            print(f"Customer {customer_id} created and payment {pix_id} registered.")
        else:
            # Atualiza tanto o novo pagamento quanto o campo last_payment_id
            table.update_item(
                Key={'customer_id': customer_id},
                UpdateExpression="SET payments.#pix_id = :payment_data, last_payment_id = :pix_id",
                ExpressionAttributeNames={
                    "#pix_id": pix_id
                },
                ExpressionAttributeValues={
                    ":payment_data": {
                        "status": "pending",
                        "amount": Decimal(str(amount)),
                        "timestamp": timestamp
                    },
                    ":pix_id": pix_id
                }
            )
            print(f"Payment {pix_id} registered and set as last payment for customer {customer_id}.")
    except Exception as e:
        print(f"Error registering payment: {e}")

def check_pix_status(customer_id, pix_id=None):
    try:
        response = table.get_item(Key={'customer_id': customer_id})
        item = response.get('Item')

        if not item:
            return "Customer not found."

        # Usa o último pagamento se nenhum for especificado
        if not pix_id:
            pix_id = item.get('last_payment_id')

        payment = item.get('payments', {}).get(pix_id)

        if payment:
            return payment.get('status', 'unknown')
        else:
            return f"Payment {pix_id} not found for customer {customer_id}."
    except Exception as e:
        print(f"Error checking status: {e}")
        return "Error"


def confirm_pix_payment(customer_id, pix_id=None):
    try:
        response = table.get_item(Key={'customer_id': customer_id})
        item = response.get('Item')

        if not item:
            print("Customer not found.")
            return

        if not pix_id:
            pix_id = item.get('last_payment_id')

        if not pix_id or pix_id not in item.get('payments', {}):
            print(f"Payment {pix_id} not found.")
            return

        table.update_item(
            Key={'customer_id': customer_id},
            UpdateExpression="SET payments.#pix_id.#status = :status",
            ExpressionAttributeNames={
                "#pix_id": pix_id,
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":status": "confirmed"
            }
        )
        print(f"Payment {pix_id} confirmed for customer {customer_id}.")
    except Exception as e:
        print(f"Error confirming payment: {e}")


# Example usage
if __name__ == "__main__":
    # create_table()
    # register_pix_payment("cliente123", "pix475", 200)
    # print(check_pix_status("cliente123", "pix315"))
    # confirm_pix_payment("cliente123")
    # print(check_pix_status("cliente123", "pix789"))
    pass

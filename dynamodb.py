import boto3
import os

is_local = os.path.exists('.env')

# Load environment variables from .env
if is_local:
    from dotenv import load_dotenv
    load_dotenv()

# Create the table (only needs to be done once)
def create_table():
    try:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'pix_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'pix_id',
                    'AttributeType': 'S'  # String
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        print("Creating table...")
        table.wait_until_exists()
        print("Table created successfully.")
    except Exception as e:
        print("Error creating table:", e)

# Register a payment
def register_pix_payment(pix_id, email):
    response = table.put_item(
        Item={
            'pix_id': pix_id,
            'email': email,
            'status': 'pending'
        }
    )
    print("Payment registered.")
    return response

# Check payment status
def check_pix_status(pix_id):
    response = table.get_item(
        Key={'pix_id': pix_id}
    )
    item = response.get('Item')
    print("Payment info:", item)
    return item

# Update payment status to 'confirmed'
def confirm_pix_payment(pix_id):
    response = table.update_item(
        Key={'pix_id': pix_id},
        UpdateExpression='SET #s = :new_status',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':new_status': 'confirmed'},
        ReturnValues="UPDATED_NEW"
    )
    print("Payment status updated.")
    return response

# Example usage
if __name__ == "__main__":

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
    # Uncomment what you want to test

    # create_table()
    # register_pix_payment("123456789", "user@example.com")
    # check_pix_payment_status("123456789")
    # confirm_pix_payment("123456789")
    pass

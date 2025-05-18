import boto3
import os
import json
from datetime import datetime
from botocore.exceptions import ClientError

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

# Create the UsersTable
def create_users_table():
    try:
        table = dynamodb.create_table(
            TableName='UsersTable',
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='UsersTable')
        print("UsersTable created successfully!")
    except ClientError as e:
        print(f"Error creating UsersTable: {e.response['Error']['Message']}")

# Create a new user
def create_user(user_data):
    table = dynamodb.Table('UsersTable')
    try:
        response = table.put_item(Item=user_data)
        print("User created successfully.")
        return response
    except ClientError as e:
        return {'error': str(e)}

# Get user info by user_id
def get_user(user_id):
    table = dynamodb.Table('UsersTable')
    try:
        response = table.get_item(Key={'user_id': user_id})
        item = response.get('Item')
        if not item:
            return {'error': 'User not found'}
        return item
    except ClientError as e:
        return {'error': str(e)}

# Update user info (partial update)
def update_user(user_id, updates: dict):
    table = dynamodb.Table('UsersTable')
    try:
        update_expr = "SET " + ", ".join(f"{k}= :{k}" for k in updates.keys())
        expr_attr_vals = {f":{k}": v for k, v in updates.items()}

        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr_vals,
            ReturnValues="UPDATED_NEW"
        )
        print("User updated successfully.")
        return response
    except ClientError as e:
        return {'error': str(e)}
    
def enroll_user_in_course(user_id, new_course_id):
    users_table = dynamodb.Table('UsersTable')
    courses_table = dynamodb.Table('CoursesTable')

    try:
        # Step 1: Get current enrolled courses
        response = users_table.get_item(Key={'user_id': user_id})
        user = response.get('Item')
        response = courses_table.get_item(Key={'courseId': new_course_id})
        course = response.get('Item')

        if not user:
            return {'error': 'User not found'}
        if not course:
            return {'error': 'Course not found'}
        
        account_type = user.get('account_type')
        course_availability = course.get('availability')

        if account_type == 'free' and course_availability == 'paid':
            return {'error': 'Subscription must be upgraded before course enrollment'}

        enrolled = user.get('courses_enrolled', [])

        # Step 2: Check for duplicate
        if new_course_id in enrolled:
            return {'message': 'Course already enrolled'}

        # Step 3: Append and update
        enrolled.append(new_course_id)

        update_response = users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET courses_enrolled = :updated',
            ExpressionAttributeValues={
                ':updated': enrolled
            },
            ReturnValues="UPDATED_NEW"
        )
        return update_response

    except ClientError as e:
        return {'error': str(e)}


# Example usage
if __name__ == "__main__":
    # Step 1: Create the table (only run once)
    # create_users_table()

    # Step 2: Create a user
    user_data = {
        "user_id": "c14bb510-e0b1-7037-0380-c38405c3b7eb",
        "email": "nicholasyukio@gmail.com",
        "account_type": "free",
        "subscription_start_date": "2025-05-01",
        "subscription_end_date": None,
        "courses_enrolled": [],
        "completed_lessons": {},
        "profile_completed": False,
        "preferences": {
            "dark_mode": False,
            "language": "en"
        },
        "created_at": datetime.utcnow().isoformat()
    }

    create_user(user_data)

    # Step 3: Get a user
    # print(get_user("abc123-sub-from-cognito"))

    # Step 4: Update a user
    # print(update_user("abc123-sub-from-cognito", {"account_type": "paid"}))

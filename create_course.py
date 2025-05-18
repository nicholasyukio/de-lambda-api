import boto3
import os
import json
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

# Function to get all courses from DynamoDB
def get_all_courses():
    try:
        table = dynamodb.Table('CoursesTable')
        response = table.scan()
        items = response.get('Items', [])
        return items
    except ClientError as e:
        return {'error': str(e)}

# Function to get course data from DynamoDB
def get_course_data(course_id):
    print(course_id)
    try:
        # Scan the table to get all items (courses)
        table = dynamodb.Table('CoursesTable')
        response = table.get_item(Key={'courseId': course_id})
        print(response)
        item = response.get('Item')
        if not item:
            return {'error': 'Coursed not found'}
        return item
    except ClientError as e:
        return {'errord': str(e)}
    
def get_lesson_data(course_id, section_id, lesson_id):
    try:
        table = dynamodb.Table('CoursesTable')
        response = table.get_item(Key={'courseId': course_id})
        course = response.get('Item')
        if not course:
            return {'error': 'Course not found'}

        sections = course.get('sections', [])
        for section in sections:
            if section.get('sectionId') == section_id:
                lessons = section.get('lessons', [])
                for lesson in lessons:
                    if lesson.get('lessonId') == lesson_id:
                        return {
                            'courseId': course_id,
                            'sectionId': section_id,
                            'lessonId': lesson_id,
                            'sectionTitle': section.get('title'),
                            'lesson': lesson
                        }

                return {'error': 'Lesson not found'}

        return {'error': 'Section not found'}

    except ClientError as e:
        return {'error': str(e)}

# Function to create a DynamoDB table
def create_table():
    try:
        # Create a new DynamoDB table
        table = dynamodb.create_table(
            TableName='CoursesTable',  # Table name
            KeySchema=[
                {
                    'AttributeName': 'courseId',  # Partition key
                    'KeyType': 'HASH'  # Partition key type
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'courseId',
                    'AttributeType': 'S'  # String type for the partition key
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        # Wait until the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName='CoursesTable')
        print("Table created successfully!")
    except ClientError as e:
        print(f"Error creating table: {e.response['Error']['Message']}")

# Function to insert course data into DynamoDB table
def insert_course_data():
    # Reference to your DynamoDB table
    table = dynamodb.Table('CoursesTable')  # Replace with your table name

    # Data to insert
    course_data = {
        "courseId": "course-178",
        "title": "Artificial Intelligence for beginners",
        "instructor": "Linus Torvals",
        "description": "AI is the new trend - come here to learn",
        "category": "Programming",
        "createdAt": "2025-04-21T15:30:00Z",
        "availability": "paid",  # Key for availability
        "sections": [
            {
                "sectionId": "sec-1",
                "title": "Getting Started",
                "lessons": [
                    {
                        "lessonId": "lesson-1",
                        "title": "Welcome and Setup",
                        "description": "Introduction to the course and how to set up your environment.",
                        "videoId": "video-1"
                    },
                    {
                        "lessonId": "lesson-2",
                        "title": "Your First C# Script",
                        "description": "Learn how to write your first C# script and run it.",
                        "videoId": "video-2"
                    }
                ]
            },
            {
                "sectionId": "sec-2",
                "title": "Data Types and Variables",
                "lessons": [
                    {
                        "lessonId": "lesson-3",
                        "title": "Numbers and Strings",
                        "description": "Understand C#'s number and string data types.",
                        "videoId": "video-3"
                    },
                    {
                        "lessonId": "lesson-4",
                        "title": "Lists and Dictionaries",
                        "description": "Learn how to work with lists and dictionaries in C#.",
                        "videoId": "video-4"
                    }
                ]
            }
        ]
    }

    # Insert data into DynamoDB table
    try:
        response = table.put_item(Item=course_data)
        print("PutItem succeeded:", json.dumps(response, indent=4))
    except ClientError as e:
        print("Error inserting item:", e.response['Error']['Message'])

if __name__ == "__main__":
    # Example usage
    # Step 1: Create the table (if needed)
    # create_table()

    # Step 2: Insert the course data into the table
    insert_course_data()

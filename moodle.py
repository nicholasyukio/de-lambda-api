import requests
import os

is_local = os.path.exists('.env')

if is_local:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env

def enroll_student(fullname, email, initial_password):
    response_status = ""
    # Moodle API endpoint for user creation
    url = 'https://curso.dominioeletrico.com.br/webservice/rest/server.php'
    token = os.getenv("MOODLE_DE_TOKEN")
    # Cohort ID and user ID to add to the cohort
    cohort_id = '2'
    # Course IDs to enroll the user in
    course_ids = ['2', '3', '4', '5', '6']
    name_parts = fullname.split()
    for i in range(len(name_parts)):
        name_parts[i] = name_parts[i].capitalize()
    first_name = name_parts[0].capitalize()
    last_name = ' '.join(name_parts[1:])
    print(f"First name: {first_name}")
    print(f"Last name: {last_name}")
    # Data to be sent in the request body
    user_data = {
        'wstoken': token,
        'wsfunction': 'core_user_create_users',
        'moodlewsrestformat': 'json',
        'users[0][username]': email.lower(),
        'users[0][password]': initial_password,
        'users[0][firstname]': first_name,
        'users[0][lastname]': last_name,
        'users[0][email]': email.lower()
    }
    # Making the POST request
    response = requests.post(url, data=user_data)
    response_status = response_status + "," + str(response.status_code)
    user_json_data = response.json()
    print("User created:", user_json_data)
    user_id = user_json_data[0]['id']
    print("User ID:", user_id)
    # Data to be sent in the request body to add user to cohort
    cohort_data = {
        'wstoken': token,
        'wsfunction': 'core_cohort_add_cohort_members',
        'moodlewsrestformat': 'json',
        'members[0][cohorttype][type]': 'id',
        'members[0][cohorttype][value]': cohort_id,
        'members[0][usertype][type]': 'id',
        'members[0][usertype][value]': str(user_id)
    }
    # Data to be sent in the request body to enroll user in courses
    enrollment_data = {
        'wstoken': token,
        'wsfunction': 'enrol_manual_enrol_users',
        'moodlewsrestformat': 'json',
        'enrolments[0][courseid]': '',  # Placeholder for course ID to be filled dynamically
        'enrolments[0][roleid]': '5',  # 5 corresponds to the student role
        'enrolments[0][userid]': str(user_id)
    }
    # Add user to cohort
    response = requests.post(url, data=cohort_data)
    response_status = response_status + "," + str(response.status_code)
    print("User added to cohort:", response.json())
    # Enroll user in each course
    for course_id in course_ids:
        enrollment_data['enrolments[0][courseid]'] = course_id
        response = requests.post(url, data=enrollment_data)
        response_status = response_status + "," + str(response.status_code)
        print("User enrolled in course", course_id, ":", response.json())
    return response_status
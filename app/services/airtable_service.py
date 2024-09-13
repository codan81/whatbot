

import logging
from pyairtable import Table
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Initialize Airtable table with personal access token
DATABASE_TKN = os.getenv("DATABASE_TKN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
table = Table(DATABASE_TKN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global dictionary to hold user responses
user_responses = {}

QUESTION_MAPPING = [
    {"question": "Hello! Welcome to this personalized health pilot program created by AHO! Are you ready to start this journey towards a healthier and more balanced lifestyle? To better guide your personalized goals, we kindly ask for a few moments of your time to answer some key questions so we can learn more about you.", "column": "Participation Consent"},
    {"question": "What is your name?", "column": "Name"},
    {"question": "What is your Email?", "column": "Email"},
    {"question": "What are your wellness concerns? Choose three of the following:", "column": "Concerns"},
    {"question": "What is your age?", "column": "Age"},
    {"question": "What is your gender?", "column": "Gender"},
    {"question": "What is your current weight?", "column": "Weight"},
    {"question": "What is your height?", "column": "Height"},
    {"question": "Do you have any diagnosed medical conditions? (Diabetes, hypertension, etc.)", "column": "Medical Conditions"},
    {"question": "Do you take any medication regularly?", "column": "Medications"},
    {"question": "Have you experienced any food allergies or intolerances?", "column": "Allergies"},
    {"question": "Have you recently taken any lab tests? (If so, which ones?)", "column": "Lab Tests"},
    {"question": "How often do you eat per day?", "column": "Meals Per Day"},
    {"question": "What types of foods do you consume most frequently?", "column": "Food Types"},
    {"question": "Do you consume processed or ultra-processed foods?", "column": "Processed Foods"},
    {"question": "Do you drink alcohol? How often?", "column": "Alcohol Consumption"},
    {"question": "Do you consume caffeine? How often?", "column": "Caffeine Consumption"},
    {"question": "Do you regularly engage in physical activity? (Walking, running, gym, etc.)", "column": "Physical Activity"},
    {"question": "How many times a week do you exercise?", "column": "Exercise Frequency"},
    {"question": "How long do you spend on each exercise session?", "column": "Exercise Duration"},
    {"question": "Do you enjoy exercising with others?", "column": "Exercise Companions"},
    {"question": "Do you engage in any meditation or Mindfulness activities? (Yoga, Pranayama, Zen, guided meditations, etc.)", "column": "Mindfulness Activities"},
    {"question": "How many times a week do you calm your mind?", "column": "Mindfulness Frequency"},
    {"question": "How long do you spend on each Mindfulness session?", "column": "Mindfulness Duration"},
    {"question": "Do you follow any regular Mindfulness practice or follow any expert in this field?", "column": "Mindfulness Practice"},
    {"question": "What is your main goal in starting this program? (Lose weight, gain muscle, improve general health, etc.)", "column": "Main Goal"},
    {"question": "What motivated you to enroll in this program?", "column": "Motivation"},
    {"question": "What is your availability to engage in physical activities?", "column": "Physical Activity Availability"},
    {"question": "Do you have any dietary preferences? (Vegetarian, vegan, etc.)", "column": "Dietary Preferences"},
    {"question": "How often would you like to receive updates and tips?", "column": "Update Frequency"}
]

# Extract questions from the mapping
QUESTIONS = [q["question"] for q in QUESTION_MAPPING]

def log_airtable_schema():
    try:
        logging.info("Logging Airtable schema")
        records = table.all()
        if records:
            available_fields = records[0]['fields'].keys()
            logging.info(f"Available fields in Airtable: {available_fields}")
        else:
            logging.info("No records found in Airtable")
    except Exception as e:
        logging.error(f"Error logging Airtable schema: {e}")


def get_user_responses(wa_id):
    try:
        logging.info(f"Retrieving user responses for User ID: {wa_id}")
        records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
        if records:
            user_responses = records[0]['fields'].get('responses', [])
            logging.info(f"User responses: {user_responses}")
            return user_responses
        logging.info(f"No responses found for User ID: {wa_id}")
        return []
    except Exception as e:
        logging.error(f"Error retrieving user responses: {e}")
        return []

def check_if_thread_exists(wa_id):
    try:
        logging.info(f"Checking if thread exists for User ID: {wa_id}")
        logging.info(f"Using Airtable Base ID: {AIRTABLE_BASE_ID}")
        logging.info(f"Using Airtable Table Name: {AIRTABLE_TABLE_NAME}")
        records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
        if records:
            logging.info(f"Thread found for Phone Number: {wa_id}")
            return records[0]['fields'].get('Thread ID')
        logging.info(f"No thread found for Phone Number: {wa_id}")
        return None
    except Exception as e:
        logging.error(f"Error checking if thread exists: {e}")
        return None

def store_thread(wa_id, thread_id):
    try:
        logging.info(f"Storing thread ID for User ID: {wa_id}")
        records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
        if records:
            record_id = records[0]['id']
            response = table.update(record_id, {'Thread ID': thread_id})
            logging.info(f"Thread ID stored for record ID: {record_id}")
        else:
            
            # Create a new record 
            response = table.create({
                'Phone Number': wa_id,
                'Thread ID': thread_id, 
                'Participation Consent': 'si', 
                'Name': 'John Doe',   
                'Concerns':'abc',
            })

            logging.info(f"New record created with thread ID for User ID: {wa_id}")
    except Exception as e:
        logging.error(f"Error storing thread ID: {e}")





def save_user_response(wa_id, question_index, message_body):
    try:
        # Log info about saving the user's response
        logging.info(f"Saving user response for User ID: {wa_id}")

        # Retrieve the current question info from QUESTION_MAPPING
        question_info = QUESTION_MAPPING[question_index]
        column_name = question_info.get("column")  # Get the Airtable column name from the question info

        # Log details about the current question and the response
        logging.info(f"Question Index: {question_index}")
        logging.info(f"Question Column: {column_name}")
        logging.info(f"Response Message Body: {message_body}")

        # Update the in-memory data structure
        if wa_id not in user_responses:
            user_responses[wa_id] = {}
        user_responses[wa_id][column_name] = message_body
        user_responses[wa_id]['Question Index'] = question_index + 1

        logging.info(f"Current user_responses dictionary: {user_responses}")

        # Update Airtable with the new response
        records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
        if records:
            record_id = records[0]['id']
            # Log available fields in Airtable
            available_fields = records[0]['fields'].keys()
            logging.info(f"Available fields in Airtable: {available_fields}")
            # Only update fields that exist in Airtable
            valid_fields = {k: v for k, v in user_responses[wa_id].items() if k in available_fields}
            logging.info(f"Valid fields to update: {valid_fields}")
            response = table.update(record_id, valid_fields)
            logging.info(f"Updated record ID: {record_id} with responses: {valid_fields}")
        else:
            user_responses[wa_id]['Phone Number'] = wa_id
            response = table.create({
                'Phone Number': wa_id,
                column_name: message_body, 
            })#(user_responses[wa_id])
            
            logging.info(f"Created new record for User ID: {wa_id} with responses: {user_responses[wa_id]}")

    except Exception as e:
        logging.error(f"Error saving user response: {e}")

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Ensure the scheduler is shut down when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Log Airtable schema at startup
log_airtable_schema()
import logging
from pyairtable import Table
import os
import requests
from dotenv import load_dotenv

from app.config import QUESTION_MAPPING  



# Load environment variables
load_dotenv()

# Initialize Airtable table with personal access token
DATABASE_TKN = os.getenv("DATABASE_TKN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
table = Table(DATABASE_TKN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
# api = Api(DATABASE_TKN) # v1
# table = Table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME) #v1
# Define Airtable API URL
AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

# Define headers for Airtable API requests
HEADERS = {
    "Authorization": f"Bearer {DATABASE_TKN}",
    "Content-Type": "application/json"
}

# Configure logging
logging.basicConfig(level=logging.INFO)

# # Global dictionary to hold user responses ()
# user_responses = {} #v1

# # Map of questions
# QUESTION_MAPPING = [
#     # {"question": "What is your Phone number?", "column": "Phone number"},
#     # {"question": "Thread ID", "column": "Thread ID"},
#     {"question": "Hello! Welcome to this personalized health pilot program created by AHO! Are you ready to start this journey towards a healthier and more balanced lifestyle? To better guide your personalized goals, we kindly ask for a few moments of your time to answer some key questions so we can learn more about you.", "column": "Participation Consent"},
#     {"question": "What is your name?", "column": "Name"},
#     {"question": "What is your Email?", "column": "Email"},
#     {"question": "What are your wellness concerns? Choose three of the following:", "column": "Concerns"},
#     {"question": "What is your age?", "column": "Age"},
#     {"question": "What is your gender?", "column": "Gender"},
#     {"question": "What is your current weight?", "column": "Weight"},
#     {"question": "What is your height?", "column": "Height"},
#     {"question": "Do you have any diagnosed medical conditions? (Diabetes, hypertension, etc.)", "column": "Medical Conditions"},
#     {"question": "Do you take any medication regularly?", "column": "Medications"},
#     {"question": "Have you experienced any food allergies or intolerances?", "column": "Allergies"},
#     {"question": "Have you recently taken any lab tests? (If so, which ones?)", "column": "Lab Tests"},
#     {"question": "How often do you eat per day?", "column": "Meals Per Day"},
#     {"question": "What types of foods do you consume most frequently?", "column": "Food Types"},
#     {"question": "Do you consume processed or ultra-processed foods?", "column": "Processed Foods"},
#     {"question": "Do you drink alcohol? How often?", "column": "Alcohol Consumption"},
#     {"question": "Do you consume caffeine? How often?", "column": "Caffeine Consumption"},
#     {"question": "Do you regularly engage in physical activity? (Walking, running, gym, etc.)", "column": "Physical Activity"},
#     {"question": "How many times a week do you exercise?", "column": "Exercise Frequency"},
#     {"question": "How long do you spend on each exercise session?", "column": "Exercise Duration"},
#     {"question": "Do you enjoy exercising with others?", "column": "Exercise Companions"},
#     {"question": "Do you engage in any meditation or Mindfulness activities? (Yoga, Pranayama, Zen, guided meditations, etc.)", "column": "Mindfulness Activities"},
#     {"question": "How many times a week do you calm your mind?", "column": "Mindfulness Frequency"},
#     {"question": "How long do you spend on each Mindfulness session?", "column": "Mindfulness Duration"},
#     {"question": "Do you follow any regular Mindfulness practice or follow any expert in this field?", "column": "Mindfulness Practice"},
#     {"question": "What is your main goal in starting this program? (Lose weight, gain muscle, improve general health, etc.)", "column": "Main Goal"},
#     {"question": "What motivated you to enroll in this program?", "column": "Motivation"},
#     {"question": "What is your availability to engage in physical activities?", "column": "Physical Activity Availability"},
#     {"question": "Do you have any dietary preferences? (Vegetarian, vegan, etc.)", "column": "Dietary Preferences"},
#     {"question": "How often would you like to receive updates and tips?", "column": "Update Frequency"}
# ]

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

def check_if_thread_exists(wa_id):
    try:
        logging.info(f"Checking if thread exists for User ID: {wa_id}")
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
            response = table.update(record_id, {'Thread ID': thread_id})  # Update Thread ID only
            logging.info(f"Thread ID stored for record ID: {record_id}")
        else:
            # Create a new record with only Phone Number and Thread ID
            response = table.create({
                'Phone Number': wa_id,
                'Thread ID': thread_id,
                'Participation Consent': "X"
            })
            logging.info(f"New record created with thread ID for User ID: {wa_id}")
    except Exception as e:
        logging.error(f"Error storing thread ID: {e}")



def update_airtable_from_txt(txt_file_path):
    try:
        # Extract phone number from the file name
        wa_id = os.path.basename(txt_file_path).split('.')[0]
        data = {'Phone Number': wa_id}

        with open(txt_file_path, mode='r') as file:
            lines = file.readlines()
            for line in lines:
                if isinstance(line, str):
                    line = line.strip()
                    if not line:
                        continue
                    for question in QUESTION_MAPPING:
                        if line.startswith(question["question"]):
                            answer = line.split(":", 1)[1].strip()
                            data[question["column"]] = answer
                            break

        # Log the data being sent to Airtable
        logging.info(f"Data to be sent to Airtable: {data}")

        # Check if the record exists in Airtable
        response = requests.get(AIRTABLE_API_URL, headers=HEADERS, params={"filterByFormula": f"{{Phone number}}='{wa_id}'"})
        response.raise_for_status()
        records = response.json().get('records', [])

        if records:
            record_id = records[0]['id']
            logging.info(f"Updating record for Phone number: {wa_id}")
            update_response = requests.patch(f"{AIRTABLE_API_URL}/{record_id}", headers=HEADERS, json={"fields": data})
            update_response.raise_for_status()
        else:
            logging.info(f"Creating new record for Phone number: {wa_id}")
            create_response = requests.post(AIRTABLE_API_URL, headers=HEADERS, json={"fields": data})
            create_response.raise_for_status()

        logging.info(f"Text file data from {txt_file_path} has been successfully updated to Airtable.")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        logging.error(f"Response content: {http_err.response.content}")
    except Exception as e:
        logging.error(f"Error updating Airtable from text file {txt_file_path}: {e}")

def process_all_files_in_directory(directory_path):
    try:
        files = [f for f in os.listdir(directory_path) if f.endswith(".txt")]
        if not files:
            logging.info(f"No text files found in directory {directory_path}.")
            return

        for filename in files:
            file_path = os.path.join(directory_path, filename)
            update_airtable_from_txt(file_path)
    except Exception as e:
        logging.error(f"Error processing files in directory {directory_path}: {e}")

# Define the path to your directory containing text files
directory_path = '/Users/israelfernandez/Desktop/whatbot/Chats_history'

# Process all files in the directory
process_all_files_in_directory(directory_path)
# Log Airtable schema at startup
log_airtable_schema()

# def get_user_responses(wa_id):
#     try:
#         logging.info(f"Retrieving user responses for User ID: {wa_id}")
#         records = table.all(formula=f"{{Phone Number}}='{wa_id}'")

#         if records:
#             user_responses[wa_id] = records[0]['fields']

#             # Initialize 'Question Index' if not present
#             if 'Question Index' not in user_responses[wa_id]:
#                 user_responses[wa_id]['Question Index'] = 0
            
#             # Define valid response keys that should be counted
#             valid_response_keys = [
#                 "Participation Consent", "Name", "Email", "Concerns", 
#                 "Age", "Gender", "Weight", "Height", "Medical Conditions", 
#                 "Medications", "Allergies", "Lab Tests", "Meals Per Day", 
#                 "Food Types", "Processed Foods", "Alcohol Consumption", 
#                 "Caffeine Consumption", "Physical Activity", "Exercise Frequency", 
#                 "Exercise Duration", "Exercise Companions", "Mindfulness Activities", 
#                 "Mindfulness Frequency", "Mindfulness Duration", "Mindfulness Practice", 
#                 "Main Goal", "Motivation", "Physical Activity Availability", 
#                 "Dietary Preferences", "Update Frequency"
#             ]

#             # Count only valid responses
#             actual_answers = [k for k in user_responses[wa_id].keys() if k in valid_response_keys]

#             # Set the Question Index based on actual answers found
#             user_responses[wa_id]['Question Index'] = len(actual_answers)

#             logging.info(f"User responses: {user_responses[wa_id]}")
#             return user_responses[wa_id]

#         logging.info(f"No responses found for User ID: {wa_id}. Starting fresh.")
#         return {'Question Index': 0}  # New user
#     except Exception as e:
#         logging.error(f"Error retrieving user responses: {e}")
#         return {}

# def check_if_thread_exists(wa_id):
#     try:
#         logging.info(f"Checking if thread exists for User ID: {wa_id}")
#         records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
#         if records:
#             logging.info(f"Thread found for Phone Number: {wa_id}")
#             return records[0]['fields'].get('Thread ID')
#         logging.info(f"No thread found for Phone Number: {wa_id}")
#         return None
#     except Exception as e:
#         logging.error(f"Error checking if thread exists: {e}")
#         return None

# def store_thread(wa_id, thread_id):
#     try:
#         logging.info(f"Storing thread ID for User ID: {wa_id}")
#         records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
        
#         if records:
#             record_id = records[0]['id']
#             response = table.update(record_id, {'Thread ID': thread_id})  # Update Thread ID only
#             logging.info(f"Thread ID stored for record ID: {record_id}")
#         else:
#             # Create a new record with only Phone Number and Thread ID
#             response = table.create({
#                 'Phone Number': wa_id,
#                 'Thread ID': thread_id,
#                 'Participation Consent': "X"
#             })
#             logging.info(f"New record created with thread ID for User ID: {wa_id}")
#     except Exception as e:
#         logging.error(f"Error storing thread ID: {e}")

# def save_user_response(wa_id, question_index, message_body):
#     try:
#         logging.info(f"Saving user response for User ID: {wa_id}")

#         if question_index < len(QUESTION_MAPPING):
#             question_info = QUESTION_MAPPING[question_index]
#             column_name = question_info["column"]

#             logging.info(f"Question Index: {question_index}")
#             logging.info(f"Question Column: {column_name}")
#             logging.info(f"Response Message Body: {message_body}")

#             #Retrieve user responses
#             get_user_responses(wa_id)

#             if wa_id not in user_responses:
#                 user_responses[wa_id] = {}

#             # Save the user's response and increment index correctly
#             user_responses[wa_id][column_name] = message_body  
#             user_responses[wa_id]['Question Index'] = question_index + 1  # Increment index

#             logging.info(f"Current user_responses dictionary: {user_responses}")

#             # Update Airtable with the user's responses
#             records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
#             if records:
#                 record_id = records[0]['id']
#                 available_fields = records[0]['fields'].keys()
#                 logging.info(f"Available fields in Airtable: {available_fields}")

#                 # Prepare update without metadata fields
#                 valid_fields = {k: v for k, v in user_responses[wa_id].items() if k in available_fields and k not in ['User ID', 'Phone Number', 'Thread ID']}
#                 logging.info(f"Valid fields to update: {valid_fields}")

#                 if valid_fields:  # Only update if there are valid fields
#                     response = table.update(record_id, valid_fields)
#                     logging.info(f"Updated record ID: {record_id} with responses: {valid_fields}")
#                 else:
#                     logging.warning("No valid fields to update in Airtable.")
#             else:
#                 # Create a record under the Phone Number if nothing around
#                 new_record = {
#                     'Phone Number': wa_id,
#                     column_name: message_body,
#                     'Question Index': question_index + 1  # Correctly set the subsequent question index
#                 }
#                 response = table.create(new_record)
#                 logging.info(f"Created new record for User ID: {wa_id} with responses: {new_record}")

#     except Exception as e:
#         logging.error(f"Error saving user response: {e}")

# # Log Airtable schema at startup
# log_airtable_schema()

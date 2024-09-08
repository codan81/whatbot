from pyairtable import Table
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

DATABASE_TKN = os.getenv("DATABASE_TKN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

# Initialize Airtable table with personal access token
table = Table(DATABASE_TKN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

def check_if_thread_exists(wa_id):
    try:
        logging.info(f"Checking if thread exists for User ID: {wa_id}")
        logging.info(f"Using Airtable Base ID: {AIRTABLE_BASE_ID}")
        logging.info(f"Using Airtable Table Name: {AIRTABLE_TABLE_NAME}")
        records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
        if records:
            logging.info(f"Thread found for Phone Number: {wa_id}")
            return records[0]['fields'].get('thread_id')
        logging.info(f"No thread found for Phone Number: {wa_id}")
        return None
    except Exception as e:
        logging.error(f"Error checking if thread exists: {e}")
        return None

def store_thread(wa_id, thread_id):
    try:
        logging.info(f"Storing thread ID: {thread_id} for User ID: {wa_id}")
        records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
        if records:
            record_id = records[0]['id']
            logging.info(f"Updating record ID: {record_id} with thread ID: {thread_id}")
            table.update(record_id, {'thread_id': thread_id})
            logging.info(f"Update response: {response}")
        else:
            logging.info(f"Creating new record for Phone Number: {wa_id} with thread ID: {thread_id}")
            response = table.create({'Phone Number': wa_id, 'thread_id': thread_id})
    except Exception as e:
        logging.error(f"Error storing thread: {e}")

def save_user_response(wa_id, message_body):
    try:
        logging.info(f"Saving user response for User ID: {wa_id}")
        records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
        if records:
            record_id = records[0]['id']
            table.update(record_id, {'Health Data': message_body})
        else:
            table.create({'User ID': wa_id, 'Health Data': message_body})
    except Exception as e:
        logging.error(f"Error saving user response: {e}")
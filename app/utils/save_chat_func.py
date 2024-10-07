import os
import logging
from datetime import datetime

# def save_conversation(wa_id, user_message, bot_response):
#     try:
#         # Directory where chat history will be saved
#         directory = "Chats_history"

#         # Create the directory if it does not exist
#         if not os.path.exists(directory):
#             os.makedirs(directory)

#         # File path based on the user's wa_id
#         file_path = os.path.join(directory, f"{wa_id}.txt")

#         # Log info about saving the conversation
#         logging.info(f"Saving conversation for User ID: {wa_id} to {file_path}")

#         # Read existing content to check for duplicates
#         if os.path.exists(file_path):
#             with open(file_path, "r") as file:
#                 existing_content = file.read()
#         else:
#             existing_content = ""

#         # Prepare the new conversation entry
#         timestamp = datetime.now().isoformat()
#         new_entry = f"Timestamp: {timestamp}\nBot: {bot_response}\n\n"#User ({wa_id}): {user_message}\n

#         # Check for duplicates
#         if new_entry not in existing_content:
#             # Append the conversation to the conversation file
#             with open(file_path, "a") as file:
#                 file.write(new_entry)
#             logging.info(f"Conversation saved for wa_id: {wa_id}")
#         else:
#             logging.info(f"Duplicate conversation entry detected for wa_id: {wa_id}, not saving.")

#     except Exception as e:
#         logging.error(f"Error saving conversation for wa_id: {wa_id}: {e}")

def save_conversation(wa_id, user_message, bot_response):
    try:
        # Directory where chat history will be saved
        directory = "Chats_history"

        # Create the directory if it does not exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # File path based on the user's wa_id
        file_path = os.path.join(directory, f"{wa_id}.txt")

        # Log info about saving the conversation
        logging.info(f"Saving conversation for User ID: {wa_id} to {file_path}")

        # Prepare the new conversation entry with timestamp
        timestamp = datetime.now().isoformat()
        new_entry = f"Timestamp: {timestamp}\nUser ({wa_id}): {user_message}\nBot: {bot_response}\n\n"

        # Only append the conversation if the user message is unique (ignoring bot repetition)
        append_entry = True

        # Check for duplicates in user message only (ignores repetitive bot responses)
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                existing_content = file.read()
                if f"User ({wa_id}): {user_message}" in existing_content:
                    append_entry = False
                    logging.info(f"Duplicate user entry detected for wa_id: {wa_id}, not saving.")
        
        if append_entry:
            # Append the conversation to the file
            with open(file_path, "a") as file:
                file.write(new_entry)
            logging.info(f"Conversation saved for wa_id: {wa_id}")

    except Exception as e:
        logging.error(f"Error saving conversation for wa_id: {wa_id}: {e}")
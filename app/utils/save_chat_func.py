import os 
import logging

def save_conversation(wa_id, message_body, response_body):
    try:
        # Directory where chat History will be saved
        directory = "Chats_history"

        # Create the directory if it does not exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # File path based on the user's wa_id
        file_path = os.path.join(directory, f"{wa_id}.txt")

        # Log info about saving the conversation
        logging.info(f"Saving conversation for User ID: {wa_id} to {file_path}")

        # Append the conversation to the convesrsation file
        with open (file_path, "a") as file:
            file.write(f"User ({wa_id}): {message_body}\n")
            file.write(f"Bot: {response_body}\n\n")

        logging.info(f"conversation saved for wa_id: {wa_id}")
    
    except Exception as e:
        logging.error(f"Error saving conversation: {e}")



        ####### To do list ########

        # add timestamp for each interaction 
        # add formula to detect to response time difference between user and bot
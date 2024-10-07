from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import logging
from datetime import datetime
from app.services.database import update_database_from_data, parse_data_from_lines, read_txt_file
from app.services.airtable_service import update_airtable_from_txt, process_all_files_in_directory, check_if_thread_exists, store_thread
from app.utils.save_chat_func import save_conversation
from app.config import QUESTION_MAPPING 

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPENAI_API_KEY)

def run_assistant(thread, name):
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message

def generate_response(message_body, wa_id, name):
    language = detect_language(message_body)
    thread_id = check_if_thread_exists(wa_id)
    print(f'the thread id:{thread_id}')
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id
        initial_message = (
            "Hello! Welcome to this personalized health pilot program created by AHO! "
            "Are you ready to start this journey toward a healthier and more balanced lifestyle? "
            "To better guide your personalized goals, we kindly ask you to take a few moments to answer some key questions and help us learn more about you. Do you agree?"
            if language == "en" else
            "¡Hola! Bienvenido a este programa piloto de salud personalizado creado por AHO. "
            "¿Estás listo para comenzar este viaje hacia un estilo de vida más saludable y equilibrado? "
            "Para guiar mejor tus objetivos personalizados, te pedimos amablemente que tomes unos momentos para responder algunas preguntas clave y ayudarnos a conocerte mejor. Estas de acuerdo?"
        )
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="assistant",
            content=initial_message,
        )
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="assistant",
            content=QUESTIONS[language][0],
        )
        bot_response = QUESTIONS[language][0]
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)
        bot_response = run_assistant(thread, name)

    # # Define the directory and file path
    directory_path = '/Users/israelfernandez/Desktop/whatbot/Chats_history'
    txt_file_path = os.path.join(directory_path, f"{wa_id}.txt")

    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    # Create or update the user's response file
    with open(txt_file_path, 'a') as file:
        timestamp = datetime.now().isoformat()
        file.write(f"Timestamp: {timestamp}\nBot: {bot_response}\n\n")
        file.write(f"Timestamp: {timestamp}\nUser ({wa_id}): {message_body}\n")
        
    # # Read the txt file to parse the data
    lines = read_txt_file(txt_file_path)
    data = parse_data_from_lines(lines, wa_id, thread_id)
   
    # Map wa_id to Phone_number
    data['Phone_number'] = wa_id

    # Print and log the data dictionary
    print("Data dictionary:", data)
    logging.info(f"Data dictionary: {data}")

    # Ensure that required fields are present
    required_fields = ['Phone_number']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    # Ensure that required fields are present
    if missing_fields:
        logging.error(f"Missing required fields in the data: {missing_fields}")
    else: 
        data["thread_id"] = thread_id
        update_database_from_data(data)

    # Parse the message body to extract data
    data = {'Phone_number': wa_id, 'thread_id': thread_id}#, 'timestamp': timestamp}
    for question in QUESTION_MAPPING:
        if message_body.startswith(question["question"]):
            answer = message_body.split(":", 1)[1].strip()
            data[question["column"]] = answer
            break

    # Print and log the updated data dictionary
    
    logging.info(f"Updated data dictionary: {data}")

   # Save structured data to the database
    try:
        update_database_from_data(data)
    except Exception as e:
        logging.error(f"Error updating database: {e}")
        
    # Update Airtable from text file
    update_airtable_from_txt(txt_file_path)

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )
    new_message = run_assistant(thread, name)

    # Save the conversation .txt (user message and bot response)
    save_conversation(wa_id, message_body, new_message)

    return new_message

# Define bilingual questions
QUESTIONS = {
    "en": [
        "Hello! Welcome to this personalized health pilot program created by AHO!, Are you ready to start this journey toward a healthier and more balanced lifestyle? ",
        "To better guide your personalized goals, we kindly ask you to take a few moments to answer some key questions and help us learn more about you. Do you agree?",
        "What is your name?",
        "What is your age?",
        "What is your weight?",
        "What is your height?",
        "Do you have any dietary restrictions?",
        "What are your fitness goals?"
    ],
    "es": [
        "¡Hola! Bienvenido a este programa piloto de salud personalizado creado por AHO. ¿Estás listo para comenzar este viaje hacia un estilo de vida más saludable y equilibrado? ",
        "Para guiar mejor tus objetivos personalizados, te pedimos amablemente que tomes unos momentos para responder algunas preguntas clave y ayudarnos a conocerte mejor. Estas de acuerdo?",
        "¿Cuál es tu nombre?",
        "¿Cuál es tu edad?",
        "¿Cuál es tu peso?",
        "¿Cuál es tu altura?",
        "¿Tienes alguna restricción dietética?",
        "¿Cuáles son tus objetivos de fitness?"
    ]
}

def detect_language(text):
    spanish_chars = "ñáéíóú"
    spanish_words = ["hola", "alo"]
    for char in spanish_chars:
        if char in text:
            return "es"
    for word in spanish_words:
        if word in text.lower():
            return "es"
    return "en"
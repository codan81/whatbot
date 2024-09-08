####### V1 ########
#### working version #####

from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPENAI_API_KEY)
# DATABASE_TKN = os.getenv("DATABASE_TKN")

def reset_threads():
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf.clear()
        logging.info("All stored threads have been cleared.")


def upload_file(path):
    try:
        # Upload a file with an "assistants" purpose
        with open(path, "rb") as file_to_upload:
            file = client.files.create(file=file_to_upload, purpose="assistants")
        
        # Check if the file was uploaded successfully
        if file and hasattr(file, 'id'):
            print(f"File uploaded successfully with ID: {file.id}")
            return file
        else:
            raise Exception("File upload failed: No file ID returned.")
    
    except Exception as e:
        print(f"An error occurred while uploading the file: {e}")
        raise

file = upload_file("/Users/israelfernandez/Desktop/whatbot/whatbot/data/Healthy Lifestyle.pdf")

def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp healthy food Assistant",
        instructions="You're a helpful WhatsApp assistant that can assist people with healthy habits and good and organic alimentation providing healthy recipes and if provided with ingredients use those ingredients to find the best recipes that fits those ingredients. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
        tools=[{"type": "file_search"}],
        model="gpt-4-1106-preview",
        #file_ids=[file.id]
    )
    print(assistant.id)
    return assistant

# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


def run_assistant(thread, name):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # instructions=f"You are having a conversation with {name}",
    )

    # Wait for completion
    # https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps#:~:text=under%20failed_at.-,Polling%20for%20updates,-In%20order%20to
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message

# Define bilingual questions
QUESTIONS = {
    "en": [
        "Hello! Welcome to this personalized health pilot program created by AHO!, Are you ready to start this journey toward a healthier and more balanced lifestyle? ",
        "To better guide your personalized goals, we kindly ask you to take a few moments to answer some key questions and help us learn more about you. Do you agree?",
        "What is your  name?",
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
    # Simple language detection based on the presence of Spanish-specific characters and words
    spanish_chars = "ñáéíóú"
    spanish_words = ["hola", "alo"]
    for char in spanish_chars:
        if char in text:
            return "es"
    for word in spanish_words:
        if word in text.lower():
            return "es"
    return "en"

def generate_response(message_body, wa_id, name):
    # Detect the language of the user's message
    language = detect_language(message_body)
    
    
  

    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id
        print(wa_id)
        print(thread_id)
        
        # Send the initial greeting message
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

        # Ask the first question in the detected language
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="assistant",
            content=QUESTIONS[language][0],
        )
        return QUESTIONS[language][0]
    
    # Otherwise, retrieve the existing thread
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )
    
    # Run the assistant and get the new message
    new_message = run_assistant(thread, name)

    return new_message






# import openai
# from openai import OpenAI
# import shelve
# from dotenv import load_dotenv
# import os
# import time
# import logging

# # Load environment variables
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
# client = OpenAI(api_key=OPENAI_API_KEY)

# # Function to upload a file
# def upload_file(path):
#     file = client.files.create(
#         file=open(path, "rb"), purpose="assistants"
#     )

# # Function to create an assistant
# def create_assistant(file):
#     assistant = client.beta.assistants.create(
#         name="WhatsApp healthy food Assistant",
#         instructions="You're a helpful WhatsApp assistant that can assist people with healthy habits and good and organic alimentation providing healthy recipes and if provided with ingredients use those ingredients to find the best recipes that fits those ingredients. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
#         tools=[{"type": "retrieval"}],
#         model="gpt-4-1106-preview",
#         file_ids=[file.id],
#     )
#     return assistant

# # Function to check if a thread exists
# def check_if_thread_exists(wa_id):
#     with shelve.open("threads_db") as threads_shelf:
#         return threads_shelf.get(wa_id, None)

# # Function to store a thread ID
# def store_thread(wa_id, thread_id):
#     with shelve.open("threads_db", writeback=True) as threads_shelf:
#         threads_shelf[wa_id] = thread_id

# # Function to reset threads
# def reset_threads():
#     with shelve.open("threads_db", writeback=True) as threads_shelf:
#         threads_shelf.clear()
#         logging.info("All stored threads have been cleared.")

# # Function to run the assistant
# def run_assistant(thread, name):
#     assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

#     run = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant.id,
#     )

#     while run.status != "completed":
#         time.sleep(0.5)
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

#     messages = client.beta.threads.messages.list(thread_id=thread.id)
#     new_message = messages.data[0].content[0].text.value
#     logging.info(f"Generated message: {new_message}")
#     return new_message

# # Function to generate a response
# def generate_response(message_body, wa_id, name):
#     thread_id = check_if_thread_exists(wa_id)

#     if thread_id is None:
#         logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
#         thread = client.beta.threads.create()
#         store_thread(wa_id, thread.id)
#         thread_id = thread.id

#         initial_message = (
#             "Hello! Welcome to this personalized health pilot program created by AHO! "
#             "Are you ready to start this journey toward a healthier and more balanced lifestyle? "
#             "To better guide your personalized goals, we kindly ask you to take a few moments to answer some key questions and help us learn more about you."
#         )
#         client.beta.threads.messages.create(
#             thread_id=thread_id,
#             role="assistant",
#             content=initial_message,
#         )
#     else:
#         logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
#         thread = client.beta.threads.retrieve(thread_id)

#     client.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=message_body,
#     )

#     new_message = run_assistant(thread, name)
#     return new_message

# # Example usage to test the initial greeting
# if __name__ == "__main__":
#     # Reset threads before testing
#     reset_threads()

#     # Test the initial greeting
#     wa_id = "16192457488"  # Replace with your test wa_id
#     name = "Test User"

#     response = generate_response("Hi, I'm here to test!", wa_id, name)
#     print(response)
#     print (wa_id)

######################################



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

def reset_threads():
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf.clear()
        logging.info("All stored threads have been cleared.")

# Run the reset_threads function for testing purposes comment out for production
reset_threads()


def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(
        file=open("/Users/israelfernandez/Desktop/whatbot/whatbot/data/Healthy Lifestyle.pdf", "rb"), purpose="assistants"
    )


def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp healthy food Assistant",
        instructions="You're a helpful WhatsApp assistant that can assist people with healthy habits and good and organic alimentation providing healthy recipes and if provided with ingredients use those ingredients to find the best recipes that fits those ingredients. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        file_ids=[file.id],
    )
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


def generate_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id
        print (wa_id)
        print (thread_id)
        # Send the initial greeting message
        initial_message = (
            "Hello! Welcome to this personalized health pilot program created by AHO! "
            "Are you ready to start this journey toward a healthier and more balanced lifestyle? "
            "To better guide your personalized goals, we kindly ask you to take a few moments to answer some key questions and help us learn more about you."
        )
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="assistant",
            content=initial_message,
        )
    
    #Otherwise, retrieve the existing thread
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


##############################################################################




# import openai
# from openai import OpenAI
# import shelve
# from dotenv import load_dotenv
# import os
# import time
# import logging


# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
# client = OpenAI(api_key=OPENAI_API_KEY)


# def upload_file(path):
#     # Upload a file with an "assistants" purpose
#     file = client.files.create(
#         file=open("/Users/israelfernandez/Desktop/whatbot/whatbot/data/Healthy Lifestyle.pdf", "rb"), purpose="assistants"
#     )


# def create_assistant(file):
#     """
#     You currently cannot set the temperature for Assistant via the API.
#     """
#     assistant = client.beta.assistants.create(
#         name="WhatsApp healthy food Assistant",
#         instructions="You're a helpful WhatsApp assistant that can assist people with healthy habits and good and organic alimentation providing healthy recipes and if provided with ingredients use those ingredients to find the best recipes that fits those ingredients. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
#         tools=[{"type": "retrieval"}],
#         model="gpt-4-1106-preview",
#         file_ids=[file.id],
#     )
#     return assistant


# # Use context manager to ensure the shelf file is closed properly
# def check_if_thread_exists(wa_id):
#     with shelve.open("threads_db") as threads_shelf:
#         return threads_shelf.get(wa_id, None)


# def store_thread(wa_id, thread_id):
#     with shelve.open("threads_db", writeback=True) as threads_shelf:
#         threads_shelf[wa_id] = thread_id


# def run_assistant(thread, name):
#     # Retrieve the Assistant
#     assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

#     # Run the assistant
#     run = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant.id,
#         # instructions=f"You are having a conversation with {name}",
#     )

#     # Wait for completion
#     # https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps#:~:text=under%20failed_at.-,Polling%20for%20updates,-In%20order%20to
#     while run.status != "completed":
#         # Be nice to the API
#         time.sleep(0.5)
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

#     # Retrieve the Messages
#     messages = client.beta.threads.messages.list(thread_id=thread.id)
#     new_message = messages.data[0].content[0].text.value
#     logging.info(f"Generated message: {new_message}")
#     return new_message


# def generate_response(message_body, wa_id, name):
#     # Check if there is already a thread_id for the wa_id
#     thread_id = check_if_thread_exists(wa_id)

#     # If a thread doesn't exist, create one and store it
#     if thread_id is None:
#         logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
#         thread = client.beta.threads.create()
#         store_thread(wa_id, thread.id)
#         thread_id = thread.id

        

#     # Otherwise, retrieve the existing thread
#     else:
#         logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
#         thread = client.beta.threads.retrieve(thread_id)

#     # Add message to thread
#     message = client.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=message_body,
#     )

#     # Run the assistant and get the new message
#     new_message = run_assistant(thread, name)

#     return new_message


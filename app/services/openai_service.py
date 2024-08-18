# ####### V1 ########
# #### working version #####

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

# def reset_threads():
#     with shelve.open("threads_db", writeback=True) as threads_shelf:
#         threads_shelf.clear()
#         logging.info("All stored threads have been cleared.")

# # Run the reset_threads function for testing purposes comment out for production
# reset_threads()


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
        # file_ids=[file.id]
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



########## V2 ##########





# import torch
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# import shelve
# from dotenv import load_dotenv
# import os
# import logging
# import warnings

# # Suppress warnings
# warnings.filterwarnings("ignore", category=FutureWarning)

# # Set logging level to ERROR to suppress INFO and WARNING messages
# logging.basicConfig(level=logging.ERROR)

# load_dotenv()

# # Define the model name
# model_name = "gpt2"  # Replace with the actual model name
# text_generator = pipeline("text-generation", model=model_name)

# # # Load the tokenizer
# # try:
# #     tokenizer = AutoTokenizer.from_pretrained(model_name)
# #     print(f"Tokenizer loaded successfully for model: {model_name}")
# # except Exception as e:
# #     print(f"Error loading tokenizer: {e}")

# # # Load the model
# # try:
# #     model = AutoModelForSequenceClassification.from_pretrained(model_name)
# #     print(f"Model loaded successfully for model: {model_name}")
# # except Exception as e:
# #     print(f"Error loading model: {e}")

# def generate_response(message_body, wa_id, name):
#     try:

#         # Generate response using the text generation pipeline
#         response = text_generator(message_body, max_length=150, truncation=True)
#         response_text = response[0]['generated_text'].strip()

#         # # Tokenize the input message
#         # inputs = tokenizer(message_body, return_tensors='pt', max_length=512, truncation=True)

#         # # Run the model to generate a response
#         # outputs = model(**inputs)
#         # logits = outputs.logits
        
#         # # Get the predicted class index
#         # response = torch.argmax(logits, dim=-1).item()  # Use .item() to get a Python number from the tensor

#         # # Convert the response to text
#         # response_text = tokenizer.decode(response, skip_special_tokens=True)

#         # Check for special tokens
#         if not response_text or '[unused' in response_text:
#             logging.error("Generated response contains special tokens or is empty.")
#             response_text = "Lo siento, no pude generar una respuesta adecuada."

#         logging.info(f"Generated message: {response_text}")
#         return response_text

#     except Exception as e:
#         logging.error(f"Error generating response: {e}")
#         return "Lo siento, ocurrió un error al generar la respuesta."

# def check_if_thread_exists(wa_id):
#     with shelve.open("threads_db") as threads_shelf:
#         return threads_shelf.get(wa_id, None)

# def store_thread(wa_id, thread_id):
#     with shelve.open("threads_db", writeback=True) as threads_shelf:
#         threads_shelf[wa_id] = thread_id

# def run_assistant(thread, name):
#     # Implement the dialog flow here
#     initial_questions = [
#         {
#            "question" : "¡Hola! Bienvenido/a este programa piloto de salud personalizado creado por AHO! ¿Estás listo/a para comenzar este viaje hacia un estilo de vida más saludable y balanceada?",
#            "expected_response" : "si_no"
#         },
#         {
#             "question" : "Para saber cómo mejor guiar tus metas personalizadas te pedimos que nos regales unos momentos de tu tiempo para contestar unas preguntas claves y aprender más sobre ti.",
#             "expected_response" : None
#         },
#         {
#             "question": "¿Cuál es tu nombre?",
#             "expected_response": "name"
#         },
#         {
#             "question": "¿Cuál es tu edad?",
#             "expected_response": "age"
#         },
#         {
#             "question": "¿Cuál es tu género?",
#             "expected": "gender"
#         }

        
#     ]

#     for question in initial_questions:
#         response = generate_response(message_body, wa_id, name)
#         print(response)  # Replace with actual message sending logic

#     # Continue with the rest of the dialog flow...

# def reset_threads():
#     with shelve.open("threads_db", writeback=True) as threads_shelf:
#         threads_shelf.clear()

# # # Example usage
# # if __name__ == "__main__":
# #     # Reset threads before testing
# #     reset_threads()

# # #     # Test the initial greeting
# # wa_id = "16192457488"  # Replace with your test wa_id
# # name = "Test User"
    
# # #Run the assistant and get the new message
# # new_message = run_assistant(wa_id, name)
# # response = generate_response("¡Hola! Bienvenido/a este programa piloto de salud personalizado creado por AHO! ¿Estás listo/a para comenzar este viaje hacia un estilo de vida más saludable y balanceada?", wa_id, name)
# #print(response)
# print(wa_id)

########## V3 ##########

# import warnings
# from transformers import BertForSequenceClassification, BertTokenizer
# import shelve

# # Suppress specific warnings from transformers library
# warnings.filterwarnings("ignore", message=".*clean_up_tokenization_spaces.*")
# warnings.filterwarnings("ignore", message=".*A parameter name that contains `beta`.*")
# warnings.filterwarnings("ignore", message=".*A parameter name that contains `gamma`.*")

# # Initialize BERT model and tokenizer
# model_name = "bert-base-uncased"
# model = BertForSequenceClassification.from_pretrained(model_name)
# tokenizer = BertTokenizer.from_pretrained(model_name)

# def generate_response(question):
#     # Your logic to generate response using the model
#     # This is a placeholder implementation
#     inputs = tokenizer(question, return_tensors="pt")
#     outputs = model(**inputs)
#     response = "Lo siento, no pude generar una respuesta adecuada."  # Placeholder response
#     return response

# initial_questions = [
#     {
#         "question": "¿Cuál es tu género?",
#         "expected": "gender"
#     }
# ]

# for question in initial_questions:
#     response = generate_response(question["question"])
#     print(response)  # Replace with actual message sending logic

# def reset_threads():
#     with shelve.open("threads_db", writeback=True) as threads_shelf:
#         threads_shelf.clear()

# # Example usage
# if __name__ == "__main__":
#     # Reset threads before testing
#     reset_threads()

#     # Test the initial greeting
#     wa_id = "16192457488"  # Replace with your test wa_id
#     name = "Test User"
    
#     # Run the assistant and get the new message
#     run_assistant()
#     response = generate_response("Hi, I'm here to test!")
#     print(response)
#     print(wa_id)


########## V4 ##########


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




# # Common functions
# def save_assistant_id(assistant_id, filename):
#     filepath = f'ids/{filename}'
#     os.makedirs(os.path.dirname(filepath), exist_ok=True)
#     with open(filepath, 'w') as file:
#         file.write(assistant_id)

# def save_file_id(file_id, filename):
#     filepath = f'ids/{filename}'
#     with open(filepath, 'w') as file:
#         file.write(file_id)

# def upload_file(filepath, purpose):
#     print('Uploading file...')
#     with open(filepath, 'rb') as file:
#         response = client.files.create(file=file, purpose=purpose)
#     return response.id

# # Function to handle assistant creation and execution
# def create_and_run_assistant(name, instructions, model, content, filename):
#     try:
#         # Create the assistant (excluding file_ids)
#         assistant = client.beta.assistants.create(
#             name=name,
#             instructions=instructions,
#             tools=[{"type": "retrieval"}],
#             model=model
#         )

#         # Save assistant ID to a file
#         save_assistant_id(assistant.id, filename=f"{filename}_id.txt")

#         # Create a thread
#         thread = client.beta.threads.create()
#         save_assistant_id(thread.id, filename=f"{filename}_thread_id.txt")

#         # Add message to thread
#         message = client.beta.threads.messages.create(
#             thread_id=thread.id,
#             role='user',
#             content=content
#         )

#         # Run the assistant
#         run = client.beta.threads.runs.create(
#             thread_id=thread.id,
#             assistant_id=assistant.id
#         )

#         print(f'Starting {name} run...')

#         # Wait for the run to complete
#         while True:
#             run_status = client.beta.threads.runs.retrieve(
#                 thread_id=thread.id,
#                 run_id=run.id
#             )
#             if run_status.status in ['completed', 'failed', 'cancelled']:
#                 print(f'Run completed with status: {run_status.status}')
#                 if run_status.status == 'failed':
#                     print(f'Error message: {getattr(run_status, "error", None)}')
#                     print(f'Error details: {getattr(run_status, "error_details", None)}')
#                     print(f'Run content: {getattr(run_status, "content", None)}')
#                 break
#             else:
#                 print(f'{name} run still in progress, waiting 5 seconds...')
#                 time.sleep(5)

#         # Fetch and print the messages after the run is completed
#         print(f'Run for {name} finished, fetching messages...')
#         messages = client.beta.threads.messages.list(thread_id=thread.id)
#         print(f'Messages from the thread for {name}:')
#         for message in messages.data:
#             # Check if the message content is text or something else
#             if hasattr(message.content[0], 'text'):
#                 print(f'{message.role.title()}: {message.content[0].text.value}')
#             else:
#                 print(f'{message.role.title()}: [Non-text content received]')

#         # Return the output for further use
#         # Make sure to check for text content before returning
#         if hasattr(messages.data[-1].content[0], 'text'):
#             return messages.data[-1].content[0].text.value  # Assuming the last message is the assistant's output
#         else:
#             print('The last message did not contain text content.')
#             return None

#     except Exception as e:
#         import traceback
#         print(f'Error in {name} assistant:')
#         print(f'Type: {type(e).__name__}')
#         print(f'Value: {str(e)}')
#         print('Traceback:')
#         traceback.print_exc()

#         return None


# # def parse_output_for_next_assistant(output):
# #     """
# #     Parses the output of one assistant to extract only the necessary part for the next assistant.
# #     """
# #     # Example: Extract only the strategy part from the first assistant's output
# #     match = re.search(r'STRATEGY INSTRUCTIONS:(.*)', output, re.DOTALL)
# #     if match:
# #         return match.group(1).strip()  # Return only the matched part
# #     return output  # If no specific part is matched, return the whole output

# # Data Analysis Assistant
# file_id = upload_file('/Users/israelfernandez/Desktop/whatbot/whatbot/data/Healthy Lifestyle.pdf', 'assistants')
# if not file_id:
#     print('Error uploading file, exiting...')
#     exit(1)


# # # Print a sample of the uploaded file content
# # with open('/Users/israelfernandez/Desktop/whatbot/whatbot/data/Healthy Lifestyle.pdf', 'r') as file:
# #     sample_content = file.read(1000)  # Read the first 1000 characters as a sample
# #     print(f'Successfully uploaded file. Sample content:\n{sample_content}')

# # print(f'File ID: {file_id}')

# data_analysis_output = create_and_run_assistant(
#     name='WhatsApp healthy food Assistant',
#     instructions='Guíar al usuario a través de un proceso de onboarding para el programa piloto de AHO! que permita recopilar información esencial sobre su estado de salud, hábitos y objetivos, con el fin de crear un plan de alimentación y bienestar personalizado..',
#     model='gpt-4-1106-preview',
#     content=f"Please analyze This is a Q&A data from the file with ID: {file_id} and based on it You're a helpful WhatsApp assistant that can assist people with healthy habits and good and organic alimentation providing healthy recipes and if provided with ingredients use those ingredients to find the best recipes that fits those ingredients. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
#     filename='data_analysis',
#     #file_ids=[file_id]
# )
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
#         print (wa_id)
#         print (thread_id)
#         # Send the initial greeting message
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
    
#     #Otherwise, retrieve the existing thread
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

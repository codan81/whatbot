import sqlite3
import logging
from datetime import datetime
import re

DATABASE_FILE = '/Users/israelfernandez/Desktop/whatbot/whatbot.db'

# Define the database schema
def initialize_database():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS WhatBot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Phone_number TEXT,
                Thread_ID TEXT,
                Participation_Consent TEXT,
                Name TEXT,
                Email TEXT,
                Concerns TEXT,
                Age TEXT,
                Gender TEXT,
                Weight TEXT,
                Height TEXT,
                Medical_Conditions TEXT,
                Medications TEXT,
                Allergies TEXT,
                Lab_Tests TEXT,
                Meals_Per_Day TEXT,
                Food_Types TEXT,
                Processed_Foods TEXT,
                Alcohol_Consumption TEXT,
                Caffeine_Consumption TEXT,
                Physical_Activity TEXT,
                Exercise_Frequency TEXT,
                Exercise_Duration TEXT,
                Exercise_Companions TEXT,
                Mindfulness_Activities TEXT,
                Mindfulness_Frequency TEXT,
                Mindfulness_Duration TEXT,
                Mindfulness_Practice TEXT,
                Main_Goal TEXT,
                Motivation TEXT,
                Physical_Activity_Availability TEXT,
                Dietary_Preferences TEXT,
                Update_Frequency TEXT
            )
        ''')
        conn.commit()
        logging.info("Database initialized successfully")

def read_txt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines



def parse_data_from_lines(lines, wa_id, thread_id):
    data = {'Phone_number': wa_id, 'Thread_ID': thread_id}  
    current_question = None  # Track what the bot is asking
    bot_prompt_accumulator = []  # Accumulate bot prompt lines

    print(f"Initial data: {data}")

    for line in lines:
        print(f"Processing line: {line.strip()}")
        
        if 'Bot' in line:  # Start of a bot prompt
            bot_prompt_accumulator.append(line.split(':', 1)[1].strip())
        elif 'User (' in line:  # Processing user response
            value = line.split(':', 1)[1].strip()
            print(f"User response detected: {value}")

            # Combine accumulated bot prompt lines into a single prompt
            bot_prompt = ' '.join(bot_prompt_accumulator).strip()
            print(f"Bot prompt detected: {bot_prompt}")
            
            # Detect what the bot is asking
            if 'Bienvenido' in bot_prompt.lower() or '¿estás listo' in bot_prompt.lower():
                current_question = 'consent'
            elif 'nombre' in bot_prompt.lower() or 'name' in bot_prompt.lower():
                current_question = 'name'
            elif 'correo electrónico' in bot_prompt.lower() or 'email' in bot_prompt.lower():
                current_question = 'email'
            elif '¿cuántos años tienes?' in bot_prompt.lower() or 'edad' in bot_prompt.lower():
                current_question = 'age'
            elif '¿cuál es tu género?' in bot_prompt.lower() or 'género' in bot_prompt.lower():
                current_question = 'gender'
            elif 'comparte tus inquietudes' in bot_prompt.lower() or 'Elige tres' in bot_prompt.lower() or 'What are your wellness concerns?' in bot_prompt.lower() or 'elige tres' in bot_prompt.lower():
                current_question = 'concerns'
                print(f"Detected concerns question: {bot_prompt}")
            elif 'peso actual' in bot_prompt.lower() or 'weight' in bot_prompt.lower():
                current_question = 'weight'
            elif 'altura' in bot_prompt.lower() or 'height' in bot_prompt.lower():
                current_question = 'height'
            elif 'condición médica' in bot_prompt.lower() or 'medical condition' in bot_prompt.lower():
                current_question = 'medical_condition'
            elif 'medicamento regularmente' in bot_prompt.lower():
                current_question = 'medication'
            elif 'alergia o intolerancia alimentaria' in bot_prompt.lower():
                current_question = 'allergy'
            elif 'análisis de laboratorio' in bot_prompt.lower():
                current_question = 'lab_tests'
            elif 'frecuencia comes al día' in bot_prompt.lower():
                current_question = 'meals_frequency'
            elif 'tipos de alimentos consumes' in bot_prompt.lower():
                current_question = 'food_types'
            elif 'alimentos procesados o ultraprocesados' in bot_prompt.lower():
                current_question = 'processed_food'
            elif 'alcohol' in bot_prompt.lower():
                current_question = 'alcohol'
            elif 'cafeína' in bot_prompt.lower():
                current_question = 'caffeine'
            elif 'actividad física' in bot_prompt.lower():
                current_question = 'physical_activity'
            elif 'veces a la semana ejercitas' in bot_prompt.lower():
                current_question = 'gym_frequency'
            elif 'tiempo pasas en cada sesión de ejercicio' in bot_prompt.lower():
                current_question = 'exercise_duration'
            elif 'ejercicio con otras personas' in bot_prompt.lower():
                current_question = 'exercise_preference'
            elif 'actividad de meditación o mindfulness' in bot_prompt.lower():
                current_question = 'mindfulness_activity'
            elif 'frecuencia sueles calmar tu mente' in bot_prompt.lower():
                current_question = 'mindfulness_frequency'
            elif 'tiempo sueles dedicarte a cada sesión de mindfulness' in bot_prompt.lower():
                current_question = 'mindfulness_duration'
            elif 'práctica regular de mindfulness' in bot_prompt.lower():
                current_question = 'mindfulness_practice'
            elif 'meta principal al comenzar este programa' in bot_prompt.lower():
                current_question = 'main_goal'
            elif 'motivó a inscribirte en este programa' in bot_prompt.lower():
                current_question = 'motivation'
            elif 'disponibilidad para participar en actividades físicas' in bot_prompt.lower():
                current_question = 'availability'
            elif 'preferencia dietética' in bot_prompt.lower():
                current_question = 'diet_preference'
            elif 'frecuencia te gustaría recibir actualizaciones' in bot_prompt.lower():
                current_question = 'update_frequency'
            else:
                current_question = None

            # Based on the current question (from the bot prompt), handle user's response
            if current_question == 'consent':
                if 'Participation_Consent' not in data and re.search(r'\b(si|no|yes|afirmativo|negativo)\b', value.lower()):
                    data['Participation_Consent'] = value
                    print(f"Participation_Consent set to: {value}")
            elif current_question == 'name':
                # Check if the value is likely a name (contains alphabetic characters and possibly spaces)
                if re.match(r'^[a-zA-Z\s]+$', value):
                    data['Name'] = value
                    print(f"Name set to: {value}")
            elif current_question == 'email':
                if '@' in value:  # Simple check for email format
                    data['Email'] = value
                    print(f"Email set to: {value}")
            elif current_question == 'age':
                if re.search(r'\d+', value):  # Extract age if a number is detected
                    data['Age'] = int(re.search(r'\d+', value).group())
                    print(f"Age set to: {data['Age']}")
            elif current_question == 'gender':
                if re.search(r'\b(men|woman|masculino|femenino|hombre|mujer|no binario|no binaria|non binary)\b', value.lower()):
                    data['Gender'] = value
                    print(f"Gender set to: {value}")
            elif current_question == 'concerns':
                data['Concerns'] = value
                print(f"Concerns set to: {value}")
            elif current_question == 'weight':
                data['Weight'] = value
                print(f"Weight set to: {value}")
            elif current_question == 'height':
                data['Height'] = value
                print(f"Height set to: {value}")
            elif current_question == 'medical_condition':
                data['Medical_Conditions'] = value
                print(f"Medical_Conditions set to: {value}")
            elif current_question == 'medication':
                data['Medications'] = value
                print(f"Medications set to: {value}")
            elif current_question == 'allergy':
                data['Allergies'] = value
                print(f"Allergies set to: {value}")
            elif current_question == 'lab_tests':
                data['Lab_Tests'] = value
                print(f"Lab_Tests set to: {value}")
            elif current_question == 'meals_frequency':
                data['Meals_Per_Day'] = value
                print(f"Meals_Frequency set to: {value}")
            elif current_question == 'food_types':
                data['Food_Types'] = value
                print(f"Food_Types set to: {value}")
            elif current_question == 'processed_food':
                data['Processed_Foods'] = value
                print(f"Processed_Food set to: {value}")
            elif current_question == 'alcohol':
                data['Alcohol_Consumption'] = value
                print(f"Alcohol set to: {value}")
            elif current_question == 'caffeine':
                data['Caffeine_Consumption'] = value
                print(f"Caffeine set to: {value}")
            elif current_question == 'physical_activity':
                data['Physical_Activity'] = value
                print(f"Physical_Activity set to: {value}")
            elif current_question == 'gym_frequency':
                data['Exercise_Frequency'] = value
                print(f"Gym_Frequency set to: {value}")
            elif current_question == 'exercise_duration':
                data['Exercise_Duration'] = value
                print(f"Exercise_Duration set to: {value}")
            elif current_question == 'exercise_preference':
                data['Exercise_Companions'] = value
                print(f"Exercise_Preference set to: {value}")
            elif current_question == 'mindfulness_activity':
                data['Mindfulness_Activities'] = value
                print(f"Mindfulness_Activity set to: {value}")
            elif current_question == 'mindfulness_frequency':
                data['Mindfulness_Frequency'] = value
                print(f"Mindfulness_Frequency set to: {value}")
            elif current_question == 'mindfulness_duration':
                data['Mindfulness_Duration'] = value
                print(f"Mindfulness_Duration set to: {value}")
            elif current_question == 'mindfulness_practice':
                data['Mindfulness_Practice'] = value
                print(f"Mindfulness_Practice set to: {value}")
            elif current_question == 'main_goal':
                data['Main_Goal'] = value
                print(f"Main_Goal set to: {value}")
            elif current_question == 'motivation':
                data['Motivation'] = value
                print(f"Motivation set to: {value}")
            elif current_question == 'availability':
                data['Physical_Activity_Availability'] = value
                print(f"Availability set to: {value}")
            elif current_question == 'diet_preference':
                data['Dietary_Preferences'] = value
                print(f"Diet_Preference set to: {value}")
            elif current_question == 'update_frequency':
                data['Update_Frequency'] = value
                print(f"Update_Frequency set to: {value}")
            else:
                data['user_message'] = value
                print(f"user_message set to: {value}")
            
            # Reset the question and accumulator after processing the user's response
            current_question = None
            bot_prompt_accumulator = []

        elif bot_prompt_accumulator:  # Continue accumulating bot prompt lines
            bot_prompt_accumulator.append(line.strip())

    print(f"Final parsed data: {data}")
    return data


def update_database_from_data(data):
    logging.info(f"Attempting to update database with data: {data}")
    
    required_fields = ['Phone_number', 'Thread_ID']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        logging.error(f"Missing required fields in the data: {missing_fields}")
        return

    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO WhatBot (
                    Phone_number, Thread_ID, Participation_Consent, Name, Email, Concerns, Age, Gender, Weight, Height, 
                    Medical_Conditions, Medications, Allergies, Lab_Tests, Meals_Per_Day, Food_Types, Processed_Foods, 
                    Alcohol_Consumption, Caffeine_Consumption, Physical_Activity, Exercise_Frequency, Exercise_Duration, 
                    Exercise_Companions, Mindfulness_Activities, Mindfulness_Frequency, Mindfulness_Duration, 
                    Mindfulness_Practice, Main_Goal, Motivation, Physical_Activity_Availability, Dietary_Preferences, 
                    Update_Frequency
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('Phone_number'),
                data.get('Thread_ID'),
                data.get('Participation_Consent'),
                data.get('Name'),
                data.get('Email'),
                data.get('Concerns'),
                data.get('Age'),
                data.get('Gender'),
                data.get('Weight'),
                data.get('Height'),
                data.get('Medical_Conditions'),
                data.get('Medications'),
                data.get('Allergies'),
                data.get('Lab_Tests'),
                data.get('Meals_Per_Day'),
                data.get('Food_Types'),
                data.get('Processed_Foods'),
                data.get('Alcohol_Consumption'),
                data.get('Caffeine_Consumption'),
                data.get('Physical_Activity'),
                data.get('Exercise_Frequency'),
                data.get('Exercise_Duration'),
                data.get('Exercise_Companions'),
                data.get('Mindfulness_Activities'),
                data.get('Mindfulness_Frequency'),
                data.get('Mindfulness_Duration'),
                data.get('Mindfulness_Practice'),
                data.get('Main_Goal'),
                data.get('Motivation'),
                data.get('Physical_Activity_Availability'),
                data.get('Dietary_Preferences'),
                data.get('Update_requency')
            ))
            conn.commit()
            logging.info("Database updated successfully.")
    except Exception as e:
        logging.error(f"Error updating database: {e}")

def get_conversation(wa_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT *
                FROM WhatBot
                WHERE wa_id = ?
                
            ''', (wa_id,))
            conversation = cursor.fetchall()
            logging.info(f"Retrieved conversation for wa_id: {wa_id}")
            return conversation
    except Exception as e:
        logging.error(f"Error retrieving conversation: {e}")
        return []

# Initialize the database
initialize_database()

# # # Example usage
# txt_file_path = '/Users/israelfernandez/Desktop/whatbot/Chats_history/16192457488.txt'
# wa_id = '16192457488'
# thread_id = 'thread_FAn98nyfXVTo16v9F17Q2EJx'

# # Read the txt file to parse the data
# lines = read_txt_file(txt_file_path)
# data = parse_data_from_lines(lines, wa_id, thread_id)
# update_database_from_data(data)






    
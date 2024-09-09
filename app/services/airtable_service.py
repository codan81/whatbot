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

QUESTION_MAPPING = [
    {"question": "¡Hola! Bienvenido/a este programa piloto de salud personalizado creado por AHO! ¿Estás listo/a para comenzar este viaje hacia un estilo de vida más saludable y balanceada? Para saber cómo mejor guiar tus metas personalizadas te pedimos que nos regales unos momentos de tu tiempo para contestar unas preguntas claves y aprender más sobre ti.", "column": None},
    {"question": "¿Cuál es tu nombre?", "column": "Name"},
    {"question": "Que preocupaciones tienes en torno a tu bienestar? Elige tres de las siguientes: A. Sobrepeso B. Altos niveles de ansiedad C. Pérdida de pelo D. Altos niveles de estrés E. Insomnia y falta de sueño de calidad F. Desorden alimenticio G. Malos hábitos alimenticios H. Falta de flexibilidad economica I. Depresión J. Falta de proposito o sentido de vida K. Soledad L. Cansancio interminable M. Alguna condición medica deshabilitante N. Falta de tiempo o voluntad O. Falta de conocimiento sobre temas de bienestar y alimentación balanceada. P. Otro (Por favor explica)", "column": "Concerns"},
    {"question": "¿Cuál es tu edad?", "column": "Age"},
    {"question": "¿Cuál es tu sexo?", "column": "Gender"},
    {"question": "¿Cuál es tu peso actual?", "column": "Weight"},
    {"question": "¿Cuál es tu altura?", "column": "Height"},
    {"question": "¿Tienes alguna condición médica diagnosticada? (Diabetes, hipertensión, etc.)", "column": "Medical Conditions"},
    {"question": "¿Tomas algún medicamento regularmente?", "column": "Medications"},
    {"question": "¿Has tenido alguna alergia o intolerancia alimentaria?", "column": "Allergies"},
    {"question": "¿Has realizado alguna prueba de laboratorio recientemente? (Si es así, ¿cuáles?)", "column": "Lab Tests"},
    {"question": "¿Con qué frecuencia comes al día?", "column": "Meals Per Day"},
    {"question": "¿Qué tipo de alimentos consumes con mayor frecuencia?", "column": "Food Types"},
    {"question": "¿Consumes alimentos procesados o ultraprocesados?", "column": "Processed Foods"},
    {"question": "¿Bebes alcohol? ¿Con qué frecuencia?", "column": "Alcohol Consumption"},
    {"question": "¿Consumes cafeína? ¿Con qué frecuencia?", "column": "Caffeine Consumption"},
    {"question": "¿Realizas alguna actividad física regularmente? (Caminar, correr, gimnasio, etc.)", "column": "Physical Activity"},
    {"question": "¿Cuántas veces a la semana haces ejercicio?", "column": "Exercise Frequency"},
    {"question": "¿Cuánto tiempo dedicas a cada sesión de ejercicio?", "column": "Exercise Duration"},
    {"question": "¿Te gusta hacer ejercicio con otras personas?", "column": "Exercise Companions"},
    {"question": "¿Realizas alguna actividad de meditación o Mindfulness? (Yoga, Pranayama, Zen, meditaciones guiadas, etc.)", "column": "Mindfulness Activities"},
    {"question": "¿Cuántas veces a la semana pones el calma a tu mente?", "column": "Mindfulness Frequency"},
    {"question": "¿Cuánto tiempo dedicas a cada sesión de Mindfulness?", "column": "Mindfulness Duration"},
    {"question": "¿Mantienes alguna practica constante de Mindfulness o sigues algún maestro o experto en estos temas?", "column": "Mindfulness Practice"},
    {"question": "¿Cuál es tu principal objetivo al iniciar este programa? (Perder peso, ganar masa muscular, mejorar la salud en general, etc.)", "column": "Main Goal"},
    {"question": "¿Qué te motivó a inscribirte en este programa?", "column": "Motivation"},
    {"question": "¿Cuál es tu disponibilidad para realizar actividades físicas?", "column": "Physical Activity Availability"},
    {"question": "¿Tienes alguna preferencia alimentaria? (Vegetariano, vegano, etc.)", "column": "Dietary Preferences"},
    {"question": "¿Con qué frecuencia prefieres recibir actualizaciones y consejos?", "column": "Update Frequency"},
    {"question": "Basado en las 2 metas de Bienestar para ti, te recomendamos las siguientes actividades para poder alcanzarlas. Por favor elija dos (2) de las siguientes opciones: Meta A: Una Dieta Balanceada; 1. *Consumir 3 comidas principales balanceadas 2. Completar un taller y aprender sobre nutrición balanceada 3. Hacerse una lavado intestinal 4. Consultar a un medico o terapeuta de bienestar o alimentación holística 5. Completar exitosamente una receta recomendada y consumirla 6. Hacerse examen para evaluar microbiota intestinal 7. Ayuno intermitente 8. No consumir ningún tipo de alimento después de las 7pm Meta B: Mantener un estado físico óptimo; 1. 3 días de ejercicio físico por semana 2. Correr 5 KM 3. Montar bicicleta por 10 KM 4. 20 vueltas nadando en piscina Meta C: Alcanzar Mindfulness; 1. 10 minutos de meditación por día 2. Dos (2) sesiones de Yoga por semana 3. Dos (2) sesiones de Qi Gong por semana 4. Una Caminata enfocada (mindfulness) por día", "column": "Wellness Activities"},
    {"question": "Basado en las selecciones de actividades, le compartimos las siguientes recomendaciones de agenda para comenzar a cementar esos nuevos hábitos saludables, y para que puedas comenzar con tu aventura de Bienestar: [**Opciones de horarios de actividades basados en las respuestas otorgadas por el usuario]", "column": "Activity Schedule"}
]

# Extract questions from the mapping
QUESTIONS = [q["question"] for q in QUESTION_MAPPING]

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

def save_user_response(wa_id, question_index, message_body):
    try:
        logging.info(f"Saving user response for User ID: {wa_id}")
        question_info = QUESTION_MAPPING[question_index]
        column_name = question_info["column"]
        
        if column_name:
            records = table.all(formula=f"{{Phone Number}}='{wa_id}'")
            if records:
                record_id = records[0]['id']
                table.update(record_id, {column_name: message_body})
            else:
                table.create({'Phone Number': wa_id, column_name: message_body})
    except Exception as e:
        logging.error(f"Error saving user response: {e}")

import sys
import os
from dotenv import load_dotenv
import logging


def load_configurations(app):
    load_dotenv()
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["YOUR_PHONE_NUMBER"] = os.getenv("YOUR_PHONE_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["RECIPIENT_WAID"] = os.getenv("RECIPIENT_WAID")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["PHONE_NUMBER_ID"] = os.getenv("PHONE_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


QUESTION_MAPPING = [
    {"question": "Hello! Welcome to this personalized health pilot program created by AHO! Are you ready to start this journey towards a healthier and more balanced lifestyle? To better guide your personalized goals, we kindly ask for a few moments of your time to answer some key questions so we can learn more about you.", "column": "Participation Consent"},
    {"question": "What is your name?", "column": "Name"},
    {"question": "What is your Email?", "column": "Email"},
    {"question": "What are your wellness concerns? Choose three of the following:", "column": "Concerns"},
    {"question": "What is your age?", "column": "Age"},
    {"question": "What is your gender?", "column": "Gender"},
    {"question": "What is your current weight?", "column": "Weight"},
    {"question": "What is your height?", "column": "Height"},
    {"question": "Do you have any diagnosed medical conditions? (Diabetes, hypertension, etc.)", "column": "Medical Conditions"},
    {"question": "Do you take any medication regularly?", "column": "Medications"},
    {"question": "Have you experienced any food allergies or intolerances?", "column": "Allergies"},
    {"question": "Have you recently taken any lab tests? (If so, which ones?)", "column": "Lab Tests"},
    {"question": "How often do you eat per day?", "column": "Meals Per Day"},
    {"question": "What types of foods do you consume most frequently?", "column": "Food Types"},
    {"question": "Do you consume processed or ultra-processed foods?", "column": "Processed Foods"},
    {"question": "Do you drink alcohol? How often?", "column": "Alcohol Consumption"},
    {"question": "Do you consume caffeine? How often?", "column": "Caffeine Consumption"},
    {"question": "Do you regularly engage in physical activity? (Walking, running, gym, etc.)", "column": "Physical Activity"},
    {"question": "How many times a week do you exercise?", "column": "Exercise Frequency"},
    {"question": "How long do you spend on each exercise session?", "column": "Exercise Duration"},
    {"question": "Do you enjoy exercising with others?", "column": "Exercise Companions"},
    {"question": "Do you engage in any meditation or Mindfulness activities? (Yoga, Pranayama, Zen, guided meditations, etc.)", "column": "Mindfulness Activities"},
    {"question": "How many times a week do you calm your mind?", "column": "Mindfulness Frequency"},
    {"question": "How long do you spend on each Mindfulness session?", "column": "Mindfulness Duration"},
    {"question": "Do you follow any regular Mindfulness practice or follow any expert in this field?", "column": "Mindfulness Practice"},
    {"question": "What is your main goal in starting this program? (Lose weight, gain muscle, improve general health, etc.)", "column": "Main Goal"},
    {"question": "What motivated you to enroll in this program?", "column": "Motivation"},
    {"question": "What is your availability to engage in physical activities?", "column": "Physical Activity Availability"},
    {"question": "Do you have any dietary preferences? (Vegetarian, vegan, etc.)", "column": "Dietary Preferences"},
    {"question": "How often would you like to receive updates and tips?", "column": "Update Frequency"}
]
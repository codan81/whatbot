# main.py
#from app.services.openai_service import reset_threads
import logging

from app import create_app

# Call the reset_threads function at the beginning for testing purposes
#reset_threads()

app = create_app()

if __name__ == "__main__":
    logging.info("Flask app started")
    
    app.run(host="0.0.0.0", port=8000)

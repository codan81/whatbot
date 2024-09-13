import sqlite3
import logging

DATABASE_FILE = 'WhatBot.db'

def create_tables():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS WhatBot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wa_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                message TEXT NOT NULL,
                role TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def save_message(wa_id, thread_id, message, role):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO WhatBot (wa_id, thread_id, message, role)
                VALUES (?, ?, ?, ?)
            ''', (wa_id, thread_id, message, role))
            conn.commit()
            logging.info(f"Message saved for wa_id: {wa_id}, thread_id: {thread_id}")
    except Exception as e:
        logging.error(f"Error saving message: {e}")

def get_conversation(wa_id):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT message, role FROM WhatBot
                WHERE wa_id = ?
                ORDER BY timestamp
            ''', (wa_id,))
            conversation = cursor.fetchall()
            logging.info(f"Retrieved conversation for wa_id: {wa_id}")
            return conversation
    except Exception as e:
        logging.error(f"Error retrieving conversation: {e}")
        return []
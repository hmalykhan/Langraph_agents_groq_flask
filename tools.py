"""Two beginner-friendly tools: one reads policy, one writes an SQLite ticket."""
import sqlite3
from pathlib import Path
from langchain_core.tools import tool

DB_PATH = Path(__file__).parent / 'complaints.db'

# FICTIONAL demo policies: this is not real university policy or RAG.
POLICIES = {
    'attendance': 'Demo policy: At least 75% attendance is required.',
    'library': 'Demo policy: Students may borrow up to 3 books for 14 days.',
    'fee': 'Demo policy: Semester fees are due before the first teaching week ends.',
}


@tool
def search_policy(topic: str) -> str:
    """Look up a university attendance, library or fee policy by topic."""
    topic = topic.lower()
    for keyword, policy in POLICIES.items():
        if keyword in topic:
            return policy
    return 'No matching policy found. Ask about attendance, library, or fees.'


@tool
def create_complaint(description: str) -> str:
    """Create a support complaint and return its saved ticket number."""
    description = description.strip()
    if len(description) < 8:
        return 'Please describe the issue in more detail before creating a complaint.'

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open'
            )
        ''')
        cursor = conn.execute(
            'INSERT INTO complaints (description) VALUES (?)',
            (description,),
        )
        ticket_id = cursor.lastrowid
        conn.commit()

    return f'Complaint created successfully. Ticket ID: {ticket_id}. Status: open.'

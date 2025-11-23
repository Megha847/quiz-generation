import sqlite3
from datetime import datetime

DB_FILE = "quiz.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Teachers
    c.execute("""CREATE TABLE IF NOT EXISTS teachers (
        username TEXT PRIMARY KEY, password TEXT
    )""")
    # Students
    c.execute("""CREATE TABLE IF NOT EXISTS students (
        username TEXT PRIMARY KEY, password TEXT
    )""")
    # MCQs
    c.execute("""CREATE TABLE IF NOT EXISTS mcqs (
        material_name TEXT, question TEXT, options TEXT, answer TEXT
    )""")
    # Responses
    c.execute("""CREATE TABLE IF NOT EXISTS responses (
        student TEXT, question TEXT, answer TEXT, timestamp TEXT
    )""")
    conn.commit()
    conn.close()

def add_teacher(username, password):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO teachers VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def verify_teacher(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM teachers WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

def add_student(username, password):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO students VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def verify_student(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

def save_mcqs(material_name, mcqs):
    conn = sqlite3.connect(DB_FILE)
    for mcq in mcqs:
        options_str = ",".join(mcq["options"])
        conn.execute("INSERT INTO mcqs VALUES (?, ?, ?, ?)", (material_name, mcq["question"], options_str, mcq["answer"]))
    conn.commit()
    conn.close()

def get_mcqs():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM mcqs")
    mcqs = [{"material": row[0], "question": row[1], "options": row[2].split(","), "answer": row[3]} for row in c.fetchall()]
    conn.close()
    return mcqs

def save_response(student, answers):
    conn = sqlite3.connect(DB_FILE)
    timestamp = datetime.now().isoformat()
    for question, answer in answers.items():
        conn.execute("INSERT INTO responses VALUES (?, ?, ?, ?)", (student, question, answer, timestamp))
    conn.commit()
    conn.close()

def get_responses():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM responses")
    responses = [{"student": row[0], "question": row[1], "answer": row[2], "timestamp": row[3]} for row in c.fetchall()]
    conn.close()
    return responses

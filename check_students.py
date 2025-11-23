from db import get_connection

def add_student(name, email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO students (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()

def get_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()
    return students

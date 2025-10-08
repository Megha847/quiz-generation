import sqlite3

DB_PATH = "quiz.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct TEXT NOT NULL
    )
    """)

    # Create students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """)

    # Create results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        student_answer TEXT,
        is_correct INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(question_id) REFERENCES questions(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ All tables created (if not already present)")

if __name__ == "__main__":
    create_tables()

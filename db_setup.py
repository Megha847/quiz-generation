import sqlite3

DB_PATH = "quiz.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Questions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL
    )
    """)

    # Students table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """)

    # Sessions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        total_qs INTEGER,
        correct_ans INTEGER,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
    """)

    # Responses table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        question_id INTEGER,
        chosen_option TEXT,
        is_correct INTEGER,
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database & tables are ready!")

if __name__ == "__main__":
    create_tables()

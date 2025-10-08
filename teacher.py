import sqlite3

DB_NAME = "quiz.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def setup_quiz():
    conn = get_connection()
    cursor = conn.cursor()

    # Create quiz_settings table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        num_questions INTEGER DEFAULT 5,
        time_limit INTEGER DEFAULT 0
    )
    """)

    # Ask teacher for settings
    try:
        num_q = int(input("👩‍🏫 Enter number of questions per student: "))
    except ValueError:
        num_q = 5  # default

    try:
        time_limit = int(input("⏳ Enter time limit in minutes (0 = no limit): "))
    except ValueError:
        time_limit = 0

    # Clear old settings
    cursor.execute("DELETE FROM quiz_settings")

    # Insert new settings
    cursor.execute("INSERT INTO quiz_settings (num_questions, time_limit) VALUES (?, ?)",
                   (num_q, time_limit))

    conn.commit()
    conn.close()
    print(f"✅ Quiz setup saved! ({num_q} questions per student, {time_limit} min limit)")

if __name__ == "__main__":
    setup_quiz()

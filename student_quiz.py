import sqlite3
import random

DB_NAME = "quiz.db"

# ---------------- DB Helper ----------------
def get_connection():
    return sqlite3.connect(DB_NAME)

# ---------------- Fetch Quiz Settings ----------------
def get_quiz_settings():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT num_questions FROM quiz_settings ORDER BY id DESC LIMIT 1")
        setting = cursor.fetchone()
        if setting:
            return setting[0]
    except sqlite3.OperationalError:
        # If table doesn't exist, return default
        return 5
    finally:
        conn.close()
    return 5

# ---------------- Fetch Random Questions ----------------
def fetch_random_questions(num_questions):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question_id, question_text, option_a, option_b, option_c, option_d, correct_option FROM questions")
    all_questions = cursor.fetchall()
    conn.close()
    if not all_questions:
        print("⚠️ No questions available in DB.")
        return []
    return random.sample(all_questions, min(num_questions, len(all_questions)))

# ---------------- Store Result ----------------
def store_result(student_name, qid, selected_option, is_correct):
    conn = get_connection()
    cursor = conn.cursor()
    # Create results table if not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            question_id INTEGER,
            selected_option TEXT,
            is_correct INTEGER
        )
    """)
    cursor.execute("INSERT INTO results (student_name, question_id, selected_option, is_correct) VALUES (?, ?, ?, ?)",
                   (student_name, qid, selected_option, is_correct))
    conn.commit()
    conn.close()

# ---------------- Run Quiz ----------------
def start_quiz():
    student_name = input("Enter your name: ").strip()
    num_questions = get_quiz_settings()
    questions = fetch_random_questions(num_questions)
    if not questions:
        return

    score = 0
    for idx, q in enumerate(questions, start=1):
        qid, text, a, b, c, d, correct = q
        print(f"\nQ{idx}: {text}")
        print(f"A) {a}\nB) {b}\nC) {c}\nD) {d}")
        answer = input("Your answer (A/B/C/D): ").strip().upper()
        is_correct = 1 if answer == correct else 0
        if is_correct:
            score += 1
            print("✅ Correct!")
        else:
            print(f"❌ Wrong! Correct answer: {correct}")
        store_result(student_name, qid, answer, is_correct)

    print(f"\n🎉 Quiz completed! Your score: {score}/{len(questions)}")

# ---------------- Main ----------------
if __name__ == "__main__":
    start_quiz()

import sqlite3

DB_PATH = "quiz.db"

def submit_quiz(student_email, answers):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get student id
    cur.execute("SELECT id FROM students WHERE email=?", (student_email,))
    student = cur.fetchone()
    if not student:
        conn.close()
        return "Student not found"
    student_id = student[0]

    total_questions = len(answers)
    correct_count = 0

    # Create session
    cur.execute("INSERT INTO sessions (student_id, total_qs, correct_ans) VALUES (?, ?, ?)",
                (student_id, total_questions, 0))
    session_id = cur.lastrowid

    # Save responses
    for qid, chosen in answers.items():
        cur.execute("SELECT correct_option FROM questions WHERE id=?", (qid,))
        correct_option = cur.fetchone()[0]
        is_correct = int(chosen == correct_option)
        correct_count += is_correct

        cur.execute("""
            INSERT INTO responses (session_id, question_id, chosen_option, is_correct)
            VALUES (?, ?, ?, ?)
        """, (session_id, qid, chosen, is_correct))

    # Update correct answers in session
    cur.execute("UPDATE sessions SET correct_ans=? WHERE id=?", (correct_count, session_id))
    conn.commit()
    conn.close()

    return {"total": total_questions, "correct": correct_count}

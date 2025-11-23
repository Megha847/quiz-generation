import sqlite3

DB_PATH = "quiz.db"

def get_teacher_dashboard():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all sessions and student info
    cur.execute("""
    SELECT s.id as session_id, st.name, st.email, s.total_qs, s.correct_ans
    FROM sessions s
    JOIN students st ON s.student_id = st.id
    """)
    sessions = cur.fetchall()
    conn.close()
    return sessions

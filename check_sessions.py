from db import get_connection

def create_session(student_id, total_qs, correct_ans):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sessions (student_id, total_qs, correct_ans)
        VALUES (?, ?, ?)
    """, (student_id, total_qs, correct_ans))
    conn.commit()
    conn.close()

def get_all_sessions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, st.name, s.total_qs, s.correct_ans, s.taken_at
        FROM sessions s
        JOIN students st ON st.id = s.student_id
        ORDER BY s.taken_at DESC
    """)
    sessions = cur.fetchall()
    conn.close()
    return sessions

import sqlite3

def show_sessions():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.session_id, st.name, st.email,
               COUNT(r.response_id) as total_qs,
               SUM(r.is_correct) as correct_ans,
               s.started_at
        FROM quiz_sessions s
        JOIN students st ON s.student_id = st.student_id
        LEFT JOIN responses r ON s.session_id = r.session_id
        GROUP BY s.session_id
        ORDER BY s.session_id
    """)
    rows = cursor.fetchall()

    if not rows:
        print("⚠️ No quiz sessions found.")
    else:
        print("📋 Quiz Session Summary:")
        print("-" * 90)
        for row in rows:
            sid, name, email, total, correct, started_at = row
            score = f"{correct}/{total}" if total else "0/0"
            print(f"Session {sid} | {name} ({email}) | Score: {score} | Started: {started_at}")
        print("-" * 90)

    conn.close()

if __name__ == "__main__":
    show_sessions()

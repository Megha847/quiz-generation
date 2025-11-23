from db import get_connection

def add_response(session_id, question_id, chosen_option, is_correct):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO responses (session_id, question_id, chosen_option, is_correct)
        VALUES (?, ?, ?, ?)
    """, (session_id, question_id, chosen_option, is_correct))
    conn.commit()
    conn.close()

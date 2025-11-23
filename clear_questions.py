from db import get_connection

def clear_questions_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM questions")
    conn.commit()
    conn.close()

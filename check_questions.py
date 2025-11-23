from db import get_connection

def add_mcqs_to_db(mcqs):
    conn = get_connection()
    cur = conn.cursor()
    for q in mcqs:
        cur.execute("""
            INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_option)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (q['question'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_option']))
    conn.commit()
    conn.close()

def get_all_mcqs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions")
    mcqs = cur.fetchall()
    conn.close()
    return mcqs

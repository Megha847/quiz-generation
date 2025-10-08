import sqlite3

def show_responses():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.response_id, r.session_id, r.question_id, r.selected_option, r.is_correct,
               q.question_text
        FROM responses r
        JOIN questions q ON r.question_id = q.question_id
        ORDER BY r.session_id, r.response_id
    """)
    rows = cursor.fetchall()

    if not rows:
        print("⚠️ No responses found yet.")
    else:
        print("📋 Saved Responses:")
        print("-" * 80)
        for row in rows:
            rid, sid, qid, selected, correct, qtext = row
            status = "✅ Correct" if correct == 1 else "❌ Wrong"
            print(f"Session {sid} | Q{qid}: {qtext}")
            print(f"   Answered: {selected} → {status}")
            print("-" * 80)

    conn.close()

if __name__ == "__main__":
    show_responses()

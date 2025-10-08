import sqlite3

conn = sqlite3.connect("quiz.db")
cursor = conn.cursor()

cursor.execute("SELECT question_id, question_text FROM questions")
rows = cursor.fetchall()

for r in rows:
    print(r)

conn.close()

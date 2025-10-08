import sqlite3

conn = sqlite3.connect("quiz.db")
cursor = conn.cursor()

# Delete all existing questions
cursor.execute("DELETE FROM questions")

conn.commit()
conn.close()

print("✅ Old questions cleared from the database!")

import sqlite3

def show_students():
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute("SELECT student_id, name, email, created_at FROM students")
    rows = cursor.fetchall()

    if not rows:
        print("⚠️ No students found in the database.")
    else:
        print("📋 Students in DB:")
        print("-" * 70)
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Created At'}")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {row[3]}")
        print("-" * 70)

    conn.close()

if __name__ == "__main__":
    show_students()

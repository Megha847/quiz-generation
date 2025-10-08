import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from llm_generate import extract_text_from_file, generate_mcqs_from_text

# -- Config
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "quiz_secret_key")
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz.db")
ALLOWED_EXT = {"pdf", "txt"}

# -- DB helpers
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def setup_tables():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER,
            topic TEXT,
            difficulty TEXT,
            question_text TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_option TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question_id INTEGER,
            selected_option TEXT,
            is_correct INTEGER,
            FOREIGN KEY(session_id) REFERENCES quiz_sessions(session_id),
            FOREIGN KEY(question_id) REFERENCES questions(question_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num_questions INTEGER NOT NULL DEFAULT 5
        )
    """)
    # ensure at least one setting row
    c.execute("SELECT COUNT(*) FROM quiz_settings")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO quiz_settings (num_questions) VALUES (5)")
    conn.commit()
    conn.close()

setup_tables()

# -- Utility: store mcqs returned by llm_generate into DB
def store_mcqs_into_db(mcqs, material_id=1, topic="Generated", difficulty="Medium"):
    if not mcqs:
        return 0
    conn = get_db_connection()
    c = conn.cursor()
    count = 0
    for q in mcqs:
        # Support multiple shapes from generator:
        # - {"question": "...", "options": [...], "answer": "A"}
        # - {"question_text": "...", "option_a": "...", ... , "correct_option": "A"}
        if "question" in q and "options" in q:
            opts = q.get("options", [])
            # make sure we have 4 options
            while len(opts) < 4:
                opts.append("N/A")
            a, b, c_opt, d = opts[:4]
            correct = q.get("answer", q.get("correct", "A"))
            # Convert to single letter if full text was returned
            if isinstance(correct, str) and len(correct) > 1:
                # try to find which option matches
                correct_letter = "A"
                for idx, opt in enumerate(opts[:4]):
                    if opt.strip().lower() == correct.strip().lower():
                        correct_letter = "ABCD"[idx]
                        break
                correct = correct_letter
            c.execute("""
                INSERT INTO questions (material_id, topic, difficulty, question_text,
                                       option_a, option_b, option_c, option_d, correct_option)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (material_id, topic, difficulty,
                  q.get("question").strip(), a, b, c_opt, d, correct))
            count += 1
        elif "question_text" in q:
            c.execute("""
                INSERT INTO questions (material_id, topic, difficulty, question_text,
                                       option_a, option_b, option_c, option_d, correct_option)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (material_id, topic, difficulty,
                  q.get("question_text"), q.get("option_a"), q.get("option_b"),
                  q.get("option_c"), q.get("option_d"), q.get("correct_option")))
            count += 1
    conn.commit()
    conn.close()
    return count

# -- Helpers
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# ---------------- Routes ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    # Student login form on index.html: name + email
    if request.method == "POST":
        name = request.form.get("name", "Guest").strip()
        email = request.form.get("email", "").strip()
        conn = get_db_connection()
        c = conn.cursor()
        # create or fetch student
        if email:
            c.execute("SELECT student_id FROM students WHERE email = ?", (email,))
            row = c.fetchone()
            if row:
                student_id = row["student_id"]
            else:
                c.execute("INSERT INTO students (name, email) VALUES (?, ?)", (name, email))
                conn.commit()
                student_id = c.lastrowid
        else:
            # If no email given, try to find by name (less reliable)
            c.execute("SELECT student_id FROM students WHERE name = ?", (name,))
            row = c.fetchone()
            if row:
                student_id = row["student_id"]
            else:
                c.execute("INSERT INTO students (name, email) VALUES (?, ?)", (name, None))
                conn.commit()
                student_id = c.lastrowid
        conn.close()
        return redirect(url_for("quiz", student_id=student_id))
    return render_template("index.html")

# Teacher main page
@app.route("/teacher")
def teacher():
    return render_template("teacher.html")

@app.route("/teacher/dashboard")
def teacher_dashboard():
    # basic summary: number of students, questions, sessions
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM students"); students = c.fetchone()["cnt"]
    c.execute("SELECT COUNT(*) as cnt FROM questions"); questions = c.fetchone()["cnt"]
    c.execute("SELECT COUNT(*) as cnt FROM quiz_sessions"); sessions = c.fetchone()["cnt"]
    conn.close()
    return render_template("teacher_dashboard.html", students=students, questions=questions, sessions=sessions)

# Upload page (must match template url_for in your index/upload links)
@app.route("/teacher/upload", methods=["GET", "POST"])
def upload_material():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No file selected", "danger")
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash("File type not allowed. Upload .pdf or .txt", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        # Extract text and call Cohere generator
        text = extract_text_from_file(save_path)
        if not text:
            flash("Could not extract text from the file.", "warning")
            return redirect(request.url)

        # num_questions fetched from settings:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT num_questions FROM quiz_settings ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        num_q = row["num_questions"] if row else 5
        conn.close()

        mcqs = generate_mcqs_from_text(text, num_questions=num_q)

        inserted = store_mcqs_into_db(mcqs, material_id=1, topic=filename, difficulty="Medium")
        if inserted > 0:
            flash(f"✅ File processed and {inserted} questions added to DB.", "success")
        else:
            flash("⚠️ No questions were added. Check logs or try a different file.", "warning")
        return redirect(url_for("teacher_dashboard"))
    return render_template("upload.html")

# Allow teacher to change number of questions per quiz
@app.route("/teacher/set_questions", methods=["GET", "POST"])
def set_questions():
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == "POST":
        try:
            num = int(request.form.get("num_questions", 5))
            c.execute("INSERT INTO quiz_settings (num_questions) VALUES (?)", (num,))
            conn.commit()
            flash(f"Number of questions set to {num}", "success")
        except Exception as e:
            flash("Invalid number", "danger")
        conn.close()
        return redirect(url_for("teacher_dashboard"))
    c.execute("SELECT num_questions FROM quiz_settings ORDER BY id DESC LIMIT 1")
    current = c.fetchone()
    conn.close()
    current_num = current["num_questions"] if current else 5
    return render_template("set_questions.html", current_num=current_num)

# Show list of MCQs (teacher)
@app.route("/teacher/mcqs")
def mcqs_list():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM questions ORDER BY question_id DESC LIMIT 200")
    rows = c.fetchall()
    conn.close()
    return render_template("mcqs.html", questions=rows)

# Student quiz page
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    student_id = request.args.get("student_id", type=int)
    if not student_id:
        return redirect(url_for("index"))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
    s = c.fetchone()
    if not s:
        conn.close()
        return "Student not found", 404
    student_name = s["name"]

    # Prevent re-attempt (simple policy)
    c.execute("SELECT session_id FROM quiz_sessions WHERE student_id = ?", (student_id,))
    existing = c.fetchone()
    if existing:
        conn.close()
        return render_template("quiz.html", already_attempted=True, student_name=student_name, questions=[])

    # create session
    c.execute("INSERT INTO quiz_sessions (student_id) VALUES (?)", (student_id,))
    session_id = c.lastrowid
    conn.commit()

    # fetch number of questions
    c.execute("SELECT num_questions FROM quiz_settings ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    num_q = row["num_questions"] if row else 5

    # select random questions
    c.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", (num_q,))
    questions = c.fetchall()
    conn.close()

    # POST should be handled by /result; keep this route for GET
    return render_template("quiz.html", student_name=student_name, questions=questions, session_id=session_id)

# Process quiz submission
@app.route("/result", methods=["POST"])
def result():
    session_id = request.form.get("session_id")
    if not session_id:
        return "Missing session id", 400

    conn = get_db_connection()
    c = conn.cursor()
    score = 0
    total = 0

    # form keys like q{question_id} or q{index} depending on template - we will handle q{question_id}
    for key, value in request.form.items():
        if key.startswith("q"):
            qid = key[1:]
            selected = value
            # ensure qid is integer
            try:
                qid_int = int(qid)
            except Exception:
                # maybe template used q{index} and included hidden question_id_{index}
                # try alternate: if key == q{index} there might be hidden input 'qid_{index}'
                continue
            c.execute("SELECT correct_option FROM questions WHERE question_id = ?", (qid_int,))
            row = c.fetchone()
            is_correct = 0
            if row and row["correct_option"] and row["correct_option"].upper() == selected.upper():
                score += 1
                is_correct = 1
            total += 1
            c.execute("INSERT INTO responses (session_id, question_id, selected_option, is_correct) VALUES (?, ?, ?, ?)",
                      (session_id, qid_int, selected, is_correct))
    conn.commit()
    conn.close()
    return render_template("result.html", score=score, total=total)

# Admin: view all sessions (simple)
@app.route("/teacher/sessions")
def sessions_list():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT qs.session_id, qs.student_id, s.name, qs.started_at
        FROM quiz_sessions qs
        LEFT JOIN students s ON s.student_id = qs.student_id
        ORDER BY qs.started_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return render_template("all_responses.html", sessions=rows)

# Show session detail
@app.route("/teacher/session/<int:session_id>")
def session_detail(session_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT r.response_id, r.question_id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
               r.selected_option, r.is_correct
        FROM responses r
        JOIN questions q ON q.question_id = r.question_id
        WHERE r.session_id = ?
    """, (session_id,))
    rows = c.fetchall()
    conn.close()
    return render_template("session_detail.html", responses=rows)

# run
if __name__ == "__main__":
    app.run(debug=True)

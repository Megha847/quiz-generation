from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from llm_generate import generate_mcqs_from_text

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

app = Flask(__name__)
app.secret_key = "dev_key_123"  # minimal secret key for flash/session

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"txt", "pdf"}

# In-memory storage for demo
teachers = {}  # {"email": {"name": ..., "email": ...}}
mcqs_storage = {}  # {"email": ["Q1", "Q2", ...]}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------ Routes ------------------
@app.route("/")
def home():
    return render_template("index.html")

# Teacher Login
@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        teachers[email] = {"name": name, "email": email}
        return redirect(url_for("teacher_dashboard", teacher_email=email))
    return render_template("teacher_login.html")

# Teacher Dashboard
@app.route("/teacher_dashboard/<teacher_email>")
def teacher_dashboard(teacher_email):
    mcqs = mcqs_storage.get(teacher_email, [])
    return render_template("teacher_dashboard.html", teacher=teachers[teacher_email], mcqs=mcqs)

# Upload Material & Generate MCQs
@app.route("/upload_material/<teacher_email>", methods=["GET", "POST"])
def upload_material(teacher_email):
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Extract text
            text = ""
            if filename.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            elif filename.endswith(".pdf"):
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""

            # Generate MCQs
            mcqs = generate_mcqs_from_text(text, COHERE_API_KEY)
            mcqs_storage[teacher_email] = mcqs

            flash("MCQs generated successfully!")
            return redirect(url_for("teacher_dashboard", teacher_email=teacher_email))
    return render_template("upload_material.html", teacher=teachers[teacher_email])

# Student Login
@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        student_name = request.form["name"]
        student_email = request.form["email"]
        flash(f"Welcome {student_name}! Quiz coming soon.")
        return redirect(url_for("home"))
    return render_template("student_login.html")

# Run app
if __name__ == "__main__":
    app.run(debug=True)

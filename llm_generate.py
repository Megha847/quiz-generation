import os
from dotenv import load_dotenv
import cohere

# Load API key from .env
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

def generate_mcqs_from_text(text, num_questions=5):
    """Generate MCQs from text using latest Cohere Chat API"""
    if not COHERE_API_KEY:
        print("⚠️ COHERE_API_KEY not found in .env file.")
        return []

    try:
        co = cohere.Client(COHERE_API_KEY)
        print("✨ Generating MCQs using Cohere (command-r-latest)... please wait.\n")

        response = co.chat(
    model="command-a",
    message=f"Generate {num_questions} multiple-choice questions (MCQs) with 4 options and correct answers from this text:\n{text}"
)

        print("✅ Response received from Cohere.\n")
        return response.text

    except Exception as e:
        print(f"⚠️ Error generating MCQs: {e}")
        return []

if __name__ == "__main__":
    user_text = input("Enter some text to generate MCQs from:\n")
    mcqs = generate_mcqs_from_text(user_text, num_questions=5)

    print("\nGenerated MCQs:\n")
    print(mcqs if mcqs else "No MCQs generated.")

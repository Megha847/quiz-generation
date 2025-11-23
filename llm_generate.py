# llm_generate.py
import cohere
import os
from dotenv import load_dotenv

# Load .env if exists
load_dotenv()

def generate_mcqs_from_text(text, api_key=None):
    """
    Generate MCQs from input text using Cohere Chat API v2.
    API key can be passed explicitly or read from .env.
    """
    if api_key is None:
        api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise ValueError("Cohere API key is missing!")

    co = cohere.ClientV2(api_key)

    prompt = f"""
    Generate 5 multiple-choice questions with options (A-D) and answers 
    from the following text. Format each question as:
    Q1: ...
    A. ...
    B. ...
    C. ...
    D. ...
    Answer: ...
    Text:
    {text}
    """

    response = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    mcqs_text = response.message.content[0].text
    mcqs = [line.strip() for line in mcqs_text.split("\n") if line.strip()]
    return mcqs

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Check Google key
google_key = os.getenv("GOOGLE_API_KEY")
print("GOOGLE_API_KEY:", google_key)



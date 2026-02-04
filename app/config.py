import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found")

# Create client 
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "models/gemini-flash-latest"
CONFIDENCE_THRESHOLD = 0.7

from dotenv import load_dotenv
import os

load_dotenv()  # Automatically looks for .env in current directory

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file.")
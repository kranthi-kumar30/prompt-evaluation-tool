import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

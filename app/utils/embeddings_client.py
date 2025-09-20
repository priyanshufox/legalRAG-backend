# app/utils/embeddings_client.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINIAI_API_KEY")
EMBED_MODEL = os.getenv("MODEL_FOR_EMBEDDING", "models/text-embedding-004")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def get_embedding(text: str):
    # returns list[float]
    try:
        result = genai.embed_content(
            model=EMBED_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error getting embedding with model {EMBED_MODEL}: {e}")
        raise e

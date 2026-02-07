import os
import json
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
import uvicorn

# --- 1. INITIALIZE THE APP ---
app = FastAPI(title="AtharvaVeda Life OS")

# EXACT Vercel URL (I copied this from your screenshot)
origins = [
    "http://localhost:3000",
    "https://atharvaveda-ku29nmhnb-yegitigvkrishna-gmailcoms-projects.vercel.app",
    "*"  # Keep this as a backup
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. CLOUD CREDENTIALS ---
QDRANT_URL = "https://3afbb0bc-aaf3-49f2-a40c-d2d2c45580bc.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.COF5HUNtq5GzENkLrZdIZDRN9FFoT_q4yy00kdeVaS8"

# CONFIG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "data", "atharva_dataset.json")
COLLECTION_NAME = "atharva_knowledge"

# Global variables for Lazy Loading
client = None
embeddings = None

# Helper function to load AI only when needed
def get_ai():
    global client, embeddings
    
    # 1. Connect to DB if not connected
    if client is None:
        print("--- CONNECTING TO CLOUD DB ---")
        try:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
        except Exception as e:
            print(f"DB Connection Failed: {e}")

    # 2. Load Model if not loaded
    if embeddings is None:
        print("--- LOADING AI MODEL (LAZY LOAD) ---")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    return client, embeddings

class UserQuery(BaseModel):
    problem: str

# --- 3. API ENDPOINTS ---

@app.get("/")
def health_check():
    # This endpoint is fast because it doesn't touch the AI
    return {"status": "Online", "message": "Atharva Veda API is running."}

@app.post("/solve")
def solve_problem(query: UserQuery):
    # Load AI now (The first user will wait a few seconds, but the server won't crash)
    db_client, ai_model = get_ai()
    
    if not ai_model or not db_client:
        return {"solutions": [], "message": "System is warming up. Please try again in 10 seconds."}

    vector = ai_model.embed_query(query.problem)
    
    results = db_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=3
    )

    if not results or results[0].score < 0.25:
        return {"solutions": [], "message": "The Veda is silent on this modern matter. Meditate on the question and try again."}

    formatted = []
    for hit in results:
        payload = hit.payload
        formatted.append({
            "title": payload['title'],
            "verse": payload['content'][:300] + "...",
            "full_text": payload['content'],
            "source": f"Book {payload['book']}, Hymn {payload['hymn_num']}",
            "score": hit.score
        })
    return {"solutions": formatted, "message": "Wisdom Found"}

@app.get("/library")
def get_library():
    if not os.path.exists(JSON_PATH):
        return {"error": "Library file not found"}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"books": data}

@app.get("/random")
def get_random_verse():
    if not os.path.exists(JSON_PATH):
        return {"error": "Library file not found"}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    random_hymn = random.choice(data)
    return {
        "title": random_hymn['title'],
        "verse": random_hymn['content'][:250] + "...",
        "source": f"Book {random_hymn['book']}, Hymn {random_hymn['hymn']}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
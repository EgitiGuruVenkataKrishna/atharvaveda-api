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

# Allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. CLOUD CREDENTIALS ---
# (Using the keys you provided)
QDRANT_URL = "https://3afbb0bc-aaf3-49f2-a40c-d2d2c45580bc.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.COF5HUNtq5GzENkLrZdIZDRN9FFoT_q4yy00kdeVaS8"

# CONFIG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# On Render, the data folder is in the root, same as main.py
JSON_PATH = os.path.join(BASE_DIR, "data", "atharva_dataset.json")
COLLECTION_NAME = "atharva_knowledge"

# --- 3. LOAD AI MODELS ---
print("--- CONNECTING TO CLOUD BRAIN ---")
try:
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
    # We load the model once when the server starts
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("--- SYSTEM READY (CLOUD MODE) ---")
except Exception as e:
    print(f"--- CONNECTION FAILED: {e} ---")

class UserQuery(BaseModel):
    problem: str

# --- 4. API ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "Online", "message": "Atharva Veda API is running."}

@app.post("/solve")
def solve_problem(query: UserQuery):
    # Convert user text to vector
    vector = embeddings.embed_query(query.problem)
    
    # Search Cloud DB
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=3
    )

    # Silence Logic
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
        return {"error": "Library file not found", "path": JSON_PATH}
    
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
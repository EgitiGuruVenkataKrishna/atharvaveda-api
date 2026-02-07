import os
import json
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
import uvicorn

# --- 1. INITIALIZE THE APP ---
app = FastAPI(title="AtharvaVeda Life OS")

# STRICT CORS (Trusts your Vercel App)
origins = [
    "http://localhost:3000",
    "https://atharvaveda-ku29nmhnb-yegitigvkrishna-gmailcoms-projects.vercel.app",
    "*" 
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

# LAZY LOADING VARIABLES
client = None
model = None

def get_resources():
    global client, model
    
    # 1. Connect to DB
    if client is None:
        print("--- CONNECTING TO CLOUD DB ---")
        try:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
        except Exception as e:
            print(f"DB Error: {e}")

    # 2. Load Lightweight AI Model
    if model is None:
        print("--- LOADING FASTEMBED (LITE MODE) ---")
        # This uses minimal RAM compared to PyTorch
        model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        # Note: We use a model compatible with our vector size or similar
        # Actually, let's stick to the exact same architecture to match your uploaded data:
        model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    return client, model

class UserQuery(BaseModel):
    problem: str

# --- 3. API ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "Online", "message": "Atharva Veda API is running (Lite Mode)."}

@app.post("/solve")
def solve_problem(query: UserQuery):
    db_client, ai_model = get_resources()
    
    if not ai_model or not db_client:
        return {"solutions": [], "message": "Warming up... Try again in 5 seconds."}

    # FastEmbed returns a generator, so we convert to list
    vector_generator = ai_model.embed([query.problem])
    vector = list(vector_generator)[0]
    
    results = db_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector.tolist(), # Convert numpy array to list
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
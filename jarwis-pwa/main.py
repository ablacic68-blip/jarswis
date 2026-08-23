import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.post("/api/jarvis")
def jarvis_endpoint(payload: dict):
    user_text = payload.get("text", "").strip()
    
    if not user_text:
        return {"reply": "Niste poslali tekst."}

    api_key = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("API_KEY")
    )
    
    if not api_key:
        return {"reply": "Greška: API ključ nije postavljen u Environment Variables na Renderu."}

    # Trenutno podržani i aktivni Gemini 2.5 modeli
    models = ["gemini-2.5-flash", "gemini-2.5-pro"]

    prompt = (
        "Odgovori izravno, točno i najkraće moguće na postavljeno pitanje. "
        "ZABRANJENO JE: pozdravljanje, uvodne fraze, navođenje tko pita i ponavljanje pitanja.\n\n"
        f"Pitanje: {user_text}"
    )

    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {"Content-Type": "application/json"}
    last_error = ""

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(url, headers=headers, json=body, timeout=12)
            data = res.json()

            if res.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    return {"reply": parts[0]["text"].strip()}

            if "error" in data:
                last_error = data["error"].get("message", "Greška u odgovoru")
        except Exception as e:
            last_error = str(e)

    return {"reply": f"API Greška: {last_error}"}

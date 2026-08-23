import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "JARVIS je aktivan!"}

@app.post("/api/jarvis")
def jarvis_endpoint(payload: dict):
    user_text = payload.get("text", "")
    
    api_key = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("API_KEY")
    )
    
    if not api_key:
        return {"reply": "Greška: Ključ nije postavljen."}

    # Najbrži Flash modeli poredani po brzini
    fast_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

    # Postavka koja prisiljava model na direktan i brz odgovor bez uvoda
    body = {
        "system_instruction": {
            "parts": [{"text": "Daj samo izravan odgovor. Nemoj pozdravljati, nemoj ponavljati pitanje i nemoj pisati tko pita."}]
        },
        "contents": [{"parts": [{"text": user_text}]}]
    }
    headers = {"Content-Type": "application/json"}

    for model in fast_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(url, headers=headers, json=body, timeout=5)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    # Vraća isključivo čist tekst odgovora
                    return {"reply": candidates[0]["content"]["parts"][0]["text"].strip()}
        except Exception:
            continue

    return {"reply": "Privremena greška u spajanju."}

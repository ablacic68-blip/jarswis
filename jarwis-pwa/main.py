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
        return {"reply": "Greška: Ključ nije postavljen na Renderu."}

    # Provjereni endpoint i model koji pouzdano radi
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }

    try:
        res = requests.post(url, headers=headers, json=body, timeout=15)
        data = res.json()
        
        if res.status_code == 200 and "candidates" in data:
            reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {"reply": reply}
        else:
            error_msg = data.get("error", {}).get("message", "Nepoznata greška API-ja")
            return {"reply": f"Google greška: {error_msg}"}
            
    except Exception as e:
        return {"reply": f"Greška spajanja: {str(e)}"}

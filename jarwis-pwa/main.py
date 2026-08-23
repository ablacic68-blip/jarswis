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
    
    # 1. OPCIJA: Ako koristiš OpenRouter (za Claude 3.5 Sonnet / Haiku)
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            res = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [{"role": "user", "content": user_text}]
                }
            )
            data = res.json()
            if "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0]["message"]["content"]
                return {"reply": reply, "model_used": "Claude 3.5 Sonnet"}
        except Exception:
            pass

    # 2. OPCIJA: Google Gemini Flash (Besplatno)
    gemini_key = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("API_KEY")
    )
    
    if gemini_key:
        # Redom isprobava najnovije Flash modele
        flash_models = ["gemini-2.0-flash", "gemini-1.5-flash"]
        
        for model in flash_models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                headers = {"Content-Type": "application/json"}
                body = {"contents": [{"parts": [{"text": user_text}]}]}
                
                res = requests.post(url, headers=headers, json=body).json()
                
                if "candidates" in res and len(res["candidates"]) > 0:
                    reply = res["candidates"][0]["content"]["parts"][0]["text"]
                    return {"reply": reply, "model_used": model}
            except Exception:
                continue

    return {"reply": "Greška: Nije pronađen valjani API ključ u Render postavama.", "model_used": "Greška"}

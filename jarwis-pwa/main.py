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
    
    # Automatski provjerava bilo koji naziv pod kojim si mogao spremiti ključ na Renderu
    api_key = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("API_KEY") or 
        os.getenv("OPENROUTER_API_KEY")
    )
    
    if not api_key:
        return {
            "reply": "Greška: API ključ nije pronađen u Render Environment postavkama. Provjeri naziv varijable.", 
            "model_used": "Nijedan"
        }
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        body = {"contents": [{"parts": [{"text": user_text}]}]}
        
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
        
        if "error" in data:
            error_msg = data['error'].get('message', 'Nepoznato')
            return {"reply": f"Google API greška: {error_msg}", "model_used": "Greška"}
            
        reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Nema odgovora.")
        return {"reply": reply, "model_used": "Gemini 1.5 Flash"}
        
    except Exception as e:
        return {"reply": f"Greška na serveru: {str(e)}", "model_used": "Greška"}

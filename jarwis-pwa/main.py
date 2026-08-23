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
    
    # Preuzimanje ključa
    api_key = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("API_KEY")
    )
    
    if not api_key:
        return {
            "reply": "Greška: Na Renderu pod 'Environment' nije dodan ključ GEMINI_API_KEY.", 
            "model_used": "Nema ključa"
        }
        
    # Slanje upita na Gemini 1.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    body = {"contents": [{"parts": [{"text": user_text}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
        
        # Prikaz točne greške koju Google vrati
        if "error" in data:
            error_code = data["error"].get("code", "")
            error_msg = data["error"].get("message", "Nepoznato")
            return {"reply": f"Google greška ({error_code}): {error_msg}", "model_used": "Greška"}
            
        if "candidates" in data and len(data["candidates"]) > 0:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"reply": reply, "model_used": "Gemini 1.5 Flash"}
            
        return {"reply": f"Neočekivan odgovor: {str(data)}", "model_used": "Greška"}
        
    except Exception as e:
        return {"reply": f"Server greška: {str(e)}", "model_used": "Greška"}

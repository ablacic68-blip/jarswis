import os
import google.generativeai as genai
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
        os.getenv("API_KEY") or 
        os.getenv("OPENROUTER_API_KEY")
    )
    
    if not api_key:
        return {"reply": "Greška: Nije pronađen API ključ u Render postavkama.", "model_used": "Nijedan"}
        
    try:
        genai.configure(api_key=api_key)
        
        # Probaj primarni model
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(user_text)
            return {"reply": response.text, "model_used": "Gemini 1.5 Flash"}
        except Exception:
            # Automatska zamjena na Pro verziju ako Flash nije dostupan
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(user_text)
            return {"reply": response.text, "model_used": "Gemini 1.5 Pro"}
            
    except Exception as e:
        return {"reply": f"Google SDK greška: {str(e)}", "model_used": "Greška"}

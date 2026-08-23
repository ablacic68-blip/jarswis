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
        os.getenv("API_KEY") or 
        os.getenv("OPENROUTER_API_KEY")
    )
    
    if not api_key:
        return {"reply": "Greška: Nije pronađen API ključ u Render postavama.", "model_used": "Nijedan"}
        
    try:
        # 1. Dohvaćamo točan popis modela koje tvoj ključ smije koristiti
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res_list = requests.get(list_url).json()
        
        if "error" in res_list:
            return {"reply": f"Google API Greška: {res_list['error'].get('message', 'Nepoznato')}", "model_used": "Greška"}
            
        # Filtriramo samo modele koji mogu generirati tekst
        available_models = [
            m["name"].replace("models/", "") 
            for m in res_list.get("models", []) 
            if "generateContent" in m.get("supportedGenerationMethods", [])
        ]
        
        if not available_models:
            return {"reply": "Greška: Nijedan model nije omogućen za ovaj API ključ. Provjeri je li omogućen Generative Language API u Google Cloud konzoli.", "model_used": "Greška"}
            
        # Uzimamo prvi dostupni model s liste (npr. gemini-2.0-flash, gemini-1.5-flash-latest...)
        chosen_model = available_models[0]
        
        # 2. Šaljemo upit tom modelu
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{chosen_model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        body = {"contents": [{"parts": [{"text": user_text}]}]}
        
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
        
        if "error" in data:
            return {"reply": f"Greška modela ({chosen_model}): {data['error'].get('message')}", "model_used": chosen_model}

        reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Nema odgovora.")
        return {"reply": reply, "model_used": chosen_model}

    except Exception as e:
        return {"reply": f"Greška na serveru: {str(e)}", "model_used": "Greška"}

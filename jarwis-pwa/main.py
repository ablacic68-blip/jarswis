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
        return {"reply": "Greška: Ključ nije postavljen u Renderu."}

    # Provjereni i najbrži besplatni modeli
    fast_models = ["gemini-1.5-flash", "gemini-2.0-flash"]

    # Sistemska uputa za direktan i brz odgovor bez uvodnog teksta
    body = {
        "system_instruction": {
            "parts": [{"text": "Odgovori izravno, kratko i točno na postavljeno pitanje. Zabranjeno je pozdravljanje, citiranje pitanja i uvodne fraze."}]
        },
        "contents": [{"parts": [{"text": user_text}]}]
    }
    headers = {"Content-Type": "application/json"}

    last_err = ""
    for model in fast_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            # Povećan timeout na 15 sekundi kako zahtjev ne bi pukao
            res = requests.post(url, headers=headers, json=body, timeout=15)
            data = res.json()
            
            if res.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return {"reply": reply}
            elif "error" in data:
                last_err = data["error"].get("message", "")
        except Exception as e:
            last_err = str(e)

    return {"reply": f"Greška poslužitelja: {last_err}"}

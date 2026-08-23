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

    # Provjereni besplatni modeli
    models = ["gemini-1.5-flash", "gemini-2.0-flash"]

    # Direktna uputa unutar samog tekstualnog zahtjeva (garantira brzinu i izravan odgovor)
    prompt = f"Odgovori izravno, kratko i bez ikakvih uvodnih fraza ili pozdrava na sljedeće: {user_text}"
    
    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {"Content-Type": "application/json"}

    last_err = ""
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(url, headers=headers, json=body, timeout=10)
            data = res.json()
            
            if res.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return {"reply": reply}
            elif "error" in data:
                last_err = data["error"].get("message", "Greška u odgovoru")
        except Exception as e:
            last_err = str(e)

    return {"reply": f"Greška poslužitelja: {last_err}"}

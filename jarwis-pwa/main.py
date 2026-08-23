import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Dozvola za pristup s Netlifyja i bilo koje druge domene
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
    user_text = payload.get("text", "").strip()
    
    if not user_text:
        return {"reply": "Niste poslali tekst."}

    # Provjera API ključa iz Render okruženja
    api_key = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("API_KEY")
    )
    
    if not api_key:
        return {"reply": "Greška: API ključ nije postavljen u Environment Variables na Renderu."}

    # Provjereni besplatni Gemini modeli
    models = ["gemini-1.5-flash", "gemini-2.0-flash"]

    # Stroga uputa koja forsira brzi i direktan odgovor bez ikakvog uvoda
    prompt = (
        "Odgovori izravno, točno i najkraće moguće na postavio pitanje. "
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
                    # Vraća samo čist i točan odgovor
                    return {"reply": parts[0]["text"].strip()}

            # Ako Google vrati grešku (npr. pogrešan ključ ili previše zahtjeva)
            if "error" in data:
                last_error = data["error"].get("message", "Greška u odgovoru")
            else:
                last_error = f"Status {res.status_code}"

        except requests.exceptions.Timeout:
            last_error = "Zahtjev je trajao predugo."
        except Exception as e:
            last_error = str(e)

    return {"reply": f"API Greška: {last_error}"}

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
        return {"reply": "Greška: GEMINI_API_KEY nije postavljen na Renderu.", "model_used": "Nema ključa"}

    models_to_try = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]

    last_error = ""

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        body = {"contents": [{"parts": [{"text": user_text}]}]}

        try:
            res = requests.post(url, headers=headers, json=body, timeout=15)
            data = res.json()

            if res.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"reply": reply, "model_used": model}
            elif "error" in data:
                last_error = f"[{model}] {data['error'].get('message', 'Greška')}"
        except Exception as e:
            last_error = str(e)

    return {"reply": f"Greška pri spajanju s Googleom: {last_error}", "model_used": "Greška"}

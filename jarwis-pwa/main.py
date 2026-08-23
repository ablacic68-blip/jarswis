import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.post("/api/jarvis")
def jarvis_endpoint(payload: dict):
    user_text = payload.get("text", "").strip()
    image_b64 = payload.get("image", None)
    mime_type = payload.get("mime_type", "image/jpeg")

    if not user_text and not image_b64:
        return {"reply": "Pošaljite poruku ili sliku."}

    api_key = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("API_KEY")
    )
    
    if not api_key:
        return {"reply": "Greška: API ključ nije postavljen na Renderu."}

    models_to_try = []
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        list_res = requests.get(list_url, timeout=5)
        if list_res.status_code == 200:
            data = list_res.json()
            for m in data.get("models", []):
                methods = [method.lower() for method in m.get("supportedGenerationMethods", [])]
                name = m.get("name", "").replace("models/", "")
                name_lower = name.lower()
                
                if "generatecontent" in methods and "gemini" in name_lower:
                    if not any(bad in name_lower for bad in ["audio", "live", "realtime", "speech", "tts", "stt", "embed"]):
                        models_to_try.append(name)
    except Exception:
        pass

    if not models_to_try:
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

    parts = []
    instruction = (
        "Tvoja uloga je JARVIS — inteligentan i praktičan sugovornik na mobitelu. "
        "Ako korisnik traži poziv, slanje poruke, otvaranje ili instalaciju aplikacije, Odgovori mu kratko i "
        "NA KRAJ ODGOVORA OBAVEZNO dodaj odgovarajući kod u uglatim zagradama:\n"
        "- Za poziv: [ACTION:CALL:broj]\n"
        "- Za SMS: [ACTION:SMS:broj:tekst_poruke]\n"
        "- Za instalaciju/otvaranje aplikacije: [ACTION:APP:naziv_aplikacije]\n\n"
    )

    if user_text:
        parts.append({"text": f"{instruction}Korisnik: {user_text}"})
    else:
        parts.append({"text": f"{instruction}Detaljno analiziraj ovu sliku i riješi zadatak s nje."})

    if image_b64:
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": image_b64
            }
        })

    body = {"contents": [{"parts": parts}]}
    headers = {"Content-Type": "application/json"}
    last_error = ""

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(url, headers=headers, json=body, timeout=15)
            data = res.json()

            if res.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
                parts_res = data["candidates"][0].get("content", {}).get("parts", [])
                if parts_res and "text" in parts_res[0]:
                    return {"reply": parts_res[0]["text"].strip()}

            if "error" in data:
                last_error = data["error"].get("message", "Greška u odgovoru")
        except Exception as e:
            last_error = str(e)

    return {"reply": f"API Greška: {last_error}"}

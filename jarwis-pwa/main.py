import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

class UserQuery(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "JARVIS je aktivan!"}

@app.post("/api/jarvis")
async def chat_with_jarvis(query: UserQuery):
    user_input = query.text
    
    heavy_keywords = ["kod", "programiraj", "skripta", "analiziraj", "izračunaj", "arhitektura"]
    if any(word in user_input.lower() for word in heavy_keywords) or len(user_input) > 250:
        model = "anthropic/claude-3.5-sonnet"
    else:
        model = "google/gemini-2.5-flash"

    try:
        response = ai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "Ti si JARVIS, osobni glasovni i tekstualni asistent. Odgovaraj kratko, izravno i točno (prikladno za glasovni izgovor na hrvatskom)."
                },
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
        return {"reply": reply, "model": model}
    except Exception as e:
        return {"reply": f"Oprostite, došlo je do pogreške: {str(e)}", "model": "error"}

import base64
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from sarvamai import SarvamAI

load_dotenv()

app = FastAPI(
    title="Smart Irrigation - Sarvam Voice API",
    version="1.0.0",
)

# Allow the Next.js Farmer PWA to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("SARVAM_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "SARVAM_API_KEY is missing from the .env file."
    )

client = SarvamAI(
    api_subscription_key=API_KEY
)


class SpeechRequest(BaseModel):
    text: str
    language: str


LANGUAGE_CODES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
}


@app.get("/")
def root():
    return {
        "service": "Sarvam Voice API",
        "status": "running",
        "languages": ["English", "Hindi", "Kannada"],
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "sarvam_configured": bool(API_KEY),
    }


@app.post("/speak")
def speak(request: SpeechRequest):

    if request.language not in LANGUAGE_CODES:
        raise HTTPException(
            status_code=400,
            detail="Supported languages: English, Hindi, Kannada",
        )

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty.",
        )

    try:
        language_code = LANGUAGE_CODES[request.language]

        audio = client.text_to_speech.convert(
            text=request.text,
            model="bulbul:v3",
            language_code=language_code,
            speaker="shubh",
        )

        combined_audio = "".join(audio.audios)

        audio_bytes = base64.b64decode(combined_audio)

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
        )

    except Exception as error:

        print("Sarvam TTS error:", error)

        raise HTTPException(
            status_code=500,
            detail=f"Sarvam TTS failed: {str(error)}",
        )
import whisper
from dotenv import load_dotenv
load_dotenv()
import os
import requests
from pydub import AudioSegment

import time

SARVAM_PIECE_SECONDS = 25  # Sarvam's max audio length per request is 30s, we use 25s to be safe
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v3")

_model = None

def load_model():
    global _model

    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL}...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Model loaded successfully.")

    return _model

def transcribe_chunk_whisper(chunk_path: str) -> str:
    model = load_model()
    result = model.transcribe(chunk_path, task="transcribe")
    return result["text"]

def _send_to_sarvam(piece_path: str, max_retries: int = 5, initial_backoff: float = 2.0) -> str:
    """Send one ≤30s WAV file to Sarvam and return the English transcript with exponential backoff retries."""
    headers = {"api-subscription-key": SARVAM_API_KEY}

    for attempt in range(max_retries):
        with open(piece_path, "rb") as f:
            files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
            data = {"model": SARVAM_STT_MODEL, "with_diarization": "false"}
            response = requests.post(
                SARVAM_STT_TRANSLATE_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=120,
            )

        if response.status_code == 429 or response.status_code >= 500:
            retry_after = response.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                wait_time = float(retry_after)
            else:
                wait_time = initial_backoff * (2 ** attempt)

            reason = "Rate limit hit (429)" if response.status_code == 429 else f"Server error ({response.status_code})"
            print(f"    [WARNING] Sarvam {reason}. Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})...")
            time.sleep(wait_time)
            continue

        if not response.ok:
            print(f"\nSarvam returned {response.status_code}")
            print(f"Response body: {response.text}\n")
            response.raise_for_status()

        return response.json().get("transcript", "")

    # If retries exhausted, perform a final request call or raise for status of the last response
    if not response.ok:
        print(f"\nSarvam retries exhausted. Returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  -> Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
            time.sleep(1)  # Brief pause between requests to prevent hitting rate limits
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()

   
    
def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Whisper or Sarvam depending on language choice.
    - english  → Whisper (local model)
    - hinglish → Sarvam (translates to English while transcribing)
    """
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)

def transcribe_all(chunks: list, language: str = "english") -> str:

    full_transcript = "" 

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):  

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk, language=language)  

        full_transcript += text + " "  

    print("Transcription complete.")

    return full_transcript.strip()  
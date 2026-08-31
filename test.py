from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all

load_dotenv()

source = "https://youtu.be/vFP1mgZ_LEY?si=DdFitiqVlitp79rY"
language = "hinglish"
chunks = process_input(source)
transcript = transcribe_all(chunks, language=language)
print("Transcript:")
print(transcript)
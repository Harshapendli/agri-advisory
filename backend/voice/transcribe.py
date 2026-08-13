from functools import lru_cache

@lru_cache(maxsize=1)
def _load_whisper():
    import whisper
    return whisper.load_model("small")

async def transcribe_audio(file_path: str, language: str = None) -> dict:
    model = _load_whisper()
    result = model.transcribe(file_path, language=language)
    return {
        "text": result["text"].strip(),
        "language": result.get("language", "en"),
    }

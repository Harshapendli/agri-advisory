import io

LANG_MAP = {"te": "te", "hi": "hi", "en": "en", "mr": "mr", "kn": "kn"}

async def text_to_speech(text: str, lang: str = "te") -> bytes:
    from gtts import gTTS
    lang_code = LANG_MAP.get(lang, "en")
    tts = gTTS(text=text[:500], lang=lang_code, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()

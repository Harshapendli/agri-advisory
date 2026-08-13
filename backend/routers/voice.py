from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import tempfile, os, io

router = APIRouter(prefix="/voice", tags=["voice"])

class TTSRequest(BaseModel):
    text: str
    lang: str = "en"

LANG_MAP = {"te": "te", "hi": "hi", "en": "en", "mr": "mr", "kn": "kn"}

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    suffix = ".webm"
    if file.filename:
        ext = os.path.splitext(file.filename)[1]
        if ext:
            suffix = ext
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        import whisper
        model = whisper.load_model("small")
        result = model.transcribe(tmp_path)
        return {
            "text": result["text"].strip(),
            "language": result.get("language", "en"),
            "duration": result.get("duration", 0)
        }
    except ImportError:
        return {"text": "Whisper not installed. Run: pip install openai-whisper", "language": "en", "error": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        os.unlink(tmp_path)

@router.post("/speak")
async def text_to_speech(req: TTSRequest):
    try:
        from gtts import gTTS
        lang_code = LANG_MAP.get(req.lang, "en")
        tts = gTTS(text=req.text[:500], lang=lang_code, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=advisory.mp3"}
        )
    except ImportError:
        raise HTTPException(status_code=503, detail="gTTS not installed. Run: pip install gtts")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

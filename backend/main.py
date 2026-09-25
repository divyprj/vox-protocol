"""
VOX//PROTOCOL :  Neural Voice Studio
FastAPI Backend Application
"""

import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .models import SynthesisRequest, SynthesisResponse, HistoryItem, AnalyticsSummary
from .database import init_db, save_generation, get_all_generations, delete_generation_record, get_analytics_metrics
from .provider import EdgeTTSProvider, AUDIO_OUTPUT_DIR, PREVIEWS_DIR
from .benchmark import run_quality_benchmark
from .translator import TranslationEngine, TranslationRequest, TranslationResponse

app = FastAPI(
    title="VOX//PROTOCOL Neural Voice Studio",
    description="High-fidelity multilingual neural text-to-speech SaaS platform",
    version="2.0.0"
)

# Enable CORS for local dev and embedded clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = EdgeTTSProvider()
translator = TranslationEngine()
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))


@app.on_event("startup")
async def on_startup():
    init_db()
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
    os.makedirs(PREVIEWS_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    # Pre-warm voice catalog
    try:
        await provider.get_voices()
    except Exception as e:
        print(f"[VOX//PROTOCOL] Warning pre-warming voice catalog: {e}")


@app.get("/api/health")
async def health_check():
    """
    Uptime and service health telemetry for container orchestration (Docker/Render/Railway).
    """
    return {
        "status": "healthy",
        "service": "VOX//PROTOCOL Neural Voice Studio",
        "version": "2.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/api/voices")
async def list_voices():
    """
    Returns curated studio voices grouped by language and gender.
    """
    voices = await provider.get_voices()
    return [
        {
            "id": v.id,
            "name": v.name,
            "locale": v.locale,
            "language": v.language,
            "country": v.country,
            "flag": v.flag,
            "gender": v.gender,
            "is_featured": v.is_featured,
            "preview_url": f"/api/preview/{v.id}"
        }
        for v in voices
    ]


@app.get("/api/preview/{voice_id}")
async def get_voice_preview(voice_id: str):
    """
    Generates or fetches an instant 3-second audio preview sample for a voice.
    """
    try:
        filename = await provider.get_or_create_preview(voice_id)
        filepath = os.path.join(PREVIEWS_DIR, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Preview not found")
        return FileResponse(filepath, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")


@app.post("/api/translate", response_model=TranslationResponse)
async def translate_text(req: TranslationRequest):
    """
    Translates input script into the target voice language with
    automatic Romanized Indic (Hinglish) transliteration support.
    """
    return await translator.translate(req)


@app.post("/api/generate", response_model=SynthesisResponse)
async def generate_speech(req: SynthesisRequest):
    """
    Synthesize text into high-fidelity neural audio.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    gen_id = f"vox_{uuid.uuid4().hex[:10]}"
    output_filename = f"{gen_id}.mp3"

    # Identify voice details
    voices = await provider.get_voices()
    voice_match = next((v for v in voices if v.id == req.voice_id), None)
    voice_name = voice_match.name if voice_match else req.voice_id
    gender = voice_match.gender if voice_match else "Unknown"
    language = voice_match.language if voice_match else "English"

    try:
        res = await provider.synthesize_speech(
            text=req.text,
            voice_id=req.voice_id,
            speed=req.speed,
            pitch=req.pitch,
            volume=req.volume,
            output_filename=output_filename,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis error: {str(e)}")

    created_at = datetime.utcnow().isoformat() + "Z"

    record = {
        "id": gen_id,
        "text": req.text,
        "voice_id": req.voice_id,
        "voice_name": voice_name,
        "gender": gender,
        "language": language,
        "filename": output_filename,
        "duration_seconds": res["duration_seconds"],
        "file_size_bytes": res["file_size_bytes"],
        "latency_ms": res["latency_ms"],
        "speed": req.speed,
        "pitch": req.pitch,
        "created_at": created_at,
    }
    save_generation(record)

    return SynthesisResponse(
        id=gen_id,
        text=req.text,
        voice_id=req.voice_id,
        voice_name=voice_name,
        gender=gender,
        language=language,
        audio_url=f"/output/{output_filename}",
        duration_seconds=res["duration_seconds"],
        file_size_bytes=res["file_size_bytes"],
        latency_ms=res["latency_ms"],
        created_at=created_at,
    )


@app.get("/api/history", response_model=List[HistoryItem])
async def get_history(limit: int = Query(50, ge=1, le=200)):
    """
    Retrieves previous speech generations with playable URLs.
    """
    rows = get_all_generations(limit=limit)
    return [
        HistoryItem(
            id=r["id"],
            text=r["text"],
            voice_id=r["voice_id"],
            voice_name=r["voice_name"],
            gender=r["gender"],
            language=r["language"],
            audio_url=f"/output/{r['filename']}",
            duration_seconds=r["duration_seconds"],
            file_size_bytes=r["file_size_bytes"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


@app.delete("/api/history/{gen_id}")
async def delete_history_item(gen_id: str):
    """
    Deletes a generated voice file and database entry.
    """
    filename = delete_generation_record(gen_id)
    if not filename:
        raise HTTPException(status_code=404, detail="Generation item not found")

    file_path = os.path.join(AUDIO_OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

    return {"success": True, "id": gen_id}


@app.get("/api/analytics", response_model=AnalyticsSummary)
async def get_analytics():
    """
    Returns platform-wide generation telemetry and efficiency metrics.
    """
    data = get_analytics_metrics()
    return AnalyticsSummary(**data)


@app.post("/api/benchmark")
async def trigger_benchmark(sample_count: int = Query(10, ge=3, le=25)):
    """
    Executes an automated multi-language synthesis benchmark measuring latency,
    Real-Time Factor (RTF), and speedup ratio.
    """
    try:
        report = await run_quality_benchmark(sample_count=sample_count)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {str(e)}")


# Serve synthesized audio files directly
app.mount("/output", StaticFiles(directory=AUDIO_OUTPUT_DIR), name="output")

# Serve frontend static assets
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "VOX//PROTOCOL API online", "docs": "/docs"})

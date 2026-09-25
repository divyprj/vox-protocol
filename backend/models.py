"""
Pydantic Data Models for VOX//PROTOCOL Voice AI SaaS Platform
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class VoiceMetadata(BaseModel):
    id: str
    name: str
    locale: str
    language: str
    gender: str
    preview_url: Optional[str] = None


class SynthesisRequest(BaseModel):
    text: str = Field(..., max_length=5000, description="Input text to synthesize into speech")
    voice_id: str = Field("en-US-JennyNeural", description="Voice identifier")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech rate multiplier (0.5x to 2.0x)")
    pitch: int = Field(0, ge=-50, le=50, description="Pitch offset in Hz (-50 to +50)")
    volume: int = Field(100, ge=0, le=100, description="Volume percentage (0 to 100)")


class SynthesisResponse(BaseModel):
    id: str
    text: str
    voice_id: str
    voice_name: str
    gender: str
    language: str
    audio_url: str
    duration_seconds: float
    file_size_bytes: int
    latency_ms: float
    created_at: str


class HistoryItem(BaseModel):
    id: str
    text: str
    voice_id: str
    voice_name: str
    gender: str
    language: str
    audio_url: str
    duration_seconds: float
    file_size_bytes: int
    created_at: str


class AnalyticsSummary(BaseModel):
    total_generations: int
    total_audio_seconds: float
    total_characters_processed: int
    mean_latency_ms: float
    mean_rtf: float
    realtime_speedup: float

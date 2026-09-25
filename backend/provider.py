"""
TTS Provider Engine for VOX//PROTOCOL
Wraps Microsoft Edge Neural TTS with multi-language catalog and tuning parameters.
"""

import asyncio
import os
import re
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import edge_tts

AUDIO_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
PREVIEWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "previews"))

# Language metadata and flags
LANGUAGE_MAP = {
    "en-US": {"lang": "English", "country": "United States", "flag": "🇺🇸"},
    "en-GB": {"lang": "English", "country": "United Kingdom", "flag": "🇬🇧"},
    "en-IN": {"lang": "English", "country": "India", "flag": "🇮🇳"},
    "hi-IN": {"lang": "Hindi", "country": "India", "flag": "🇮🇳"},
    "es-ES": {"lang": "Spanish", "country": "Spain", "flag": "🇪🇸"},
    "fr-FR": {"lang": "French", "country": "France", "flag": "🇫🇷"},
    "de-DE": {"lang": "German", "country": "Germany", "flag": "🇩🇪"},
    "ja-JP": {"lang": "Japanese", "country": "Japan", "flag": "🇯🇵"},
    "zh-CN": {"lang": "Mandarin", "country": "China", "flag": "🇨🇳"},
}

# Preferred default voices per locale
FEATURED_VOICE_IDS = {
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "en-IN-NeerjaNeural",
    "en-IN-PrabhatNeural",
    "hi-IN-SwaraNeural",
    "hi-IN-MadhurNeural",
    "es-ES-ElviraNeural",
    "es-ES-AlvaroNeural",
    "fr-FR-DeniseNeural",
    "fr-FR-HenriNeural",
    "de-DE-KatjaNeural",
    "de-DE-ConradNeural",
    "ja-JP-NanamiNeural",
    "ja-JP-KeitaNeural",
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-YunxiNeural",
}


@dataclass
class VoiceInfo:
    id: str
    name: str
    locale: str
    language: str
    country: str
    flag: str
    gender: str
    is_featured: bool


class EdgeTTSProvider:
    def __init__(self):
        self._cached_voices: Optional[List[VoiceInfo]] = None
        os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
        os.makedirs(PREVIEWS_DIR, exist_ok=True)

    async def get_voices(self) -> List[VoiceInfo]:
        """
        Dynamically fetches and caches Edge Neural voices for supported target locales.
        """
        if self._cached_voices is not None:
            return self._cached_voices

        raw_voices = await edge_tts.list_voices()
        catalog: List[VoiceInfo] = []

        for v in raw_voices:
            loc = v.get("Locale", "")
            if loc in LANGUAGE_MAP:
                short_name = v.get("ShortName", "")
                friendly_name = v.get("FriendlyName", short_name)
                # Parse clean human name e.g. "Microsoft Jenny Online (Natural) - English (United States)" -> "Jenny"
                match = re.search(r"Microsoft\s+(\w+)\s+", friendly_name)
                clean_name = match.group(1) if match else short_name.split("-")[-1].replace("Neural", "")

                gender = v.get("Gender", "Unknown")
                meta = LANGUAGE_MAP[loc]

                catalog.append(
                    VoiceInfo(
                        id=short_name,
                        name=clean_name,
                        locale=loc,
                        language=meta["lang"],
                        country=meta["country"],
                        flag=meta["flag"],
                        gender=gender,
                        is_featured=(short_name in FEATURED_VOICE_IDS),
                    )
                )

        # Sort featured first, then alphabetical by language and name
        catalog.sort(key=lambda x: (not x.is_featured, x.language, x.gender, x.name))
        self._cached_voices = catalog
        return self._cached_voices

    async def synthesize_speech(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0,
        pitch: int = 0,
        volume: int = 100,
        output_filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes text into high-fidelity speech using Edge TTS.
        """
        if not output_filename:
            output_filename = f"vox_{int(time.time() * 1000)}.mp3"

        out_path = os.path.join(AUDIO_OUTPUT_DIR, output_filename)

        # Format rate, pitch, and volume for SSML / Edge TTS
        # speed: 1.0 -> "+0%", 1.5 -> "+50%", 0.75 -> "-25%"
        rate_int = round((speed - 1.0) * 100)
        rate_str = f"+{rate_int}%" if rate_int >= 0 else f"{rate_int}%"

        # pitch: 0 -> "+0Hz", 15 -> "+15Hz"
        pitch_str = f"+{pitch}Hz" if pitch >= 0 else f"{pitch}Hz"

        # volume: 100 -> "+0%", 80 -> "-20%"
        vol_offset = volume - 100
        vol_str = f"+{vol_offset}%" if vol_offset >= 0 else f"{vol_offset}%"

        start_time = time.perf_counter()

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice_id,
            rate=rate_str,
            pitch=pitch_str,
            volume=vol_str,
        )
        await communicate.save(out_path)

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        file_size = os.path.getsize(out_path)

        # Duration estimation (or via mutagen/wave/ffprobe if available)
        # Average bitrate of Edge TTS MP3 is ~48kbps or 64kbps (6000-8000 bytes/sec)
        # For precise duration, try ffprobe or MP3 header calculation
        duration_sec = max(0.5, file_size / 6000.0)

        try:
            import subprocess
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", out_path]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            if res.stdout.strip():
                duration_sec = float(res.stdout.strip())
        except Exception:
            pass

        return {
            "file_path": out_path,
            "filename": output_filename,
            "file_size_bytes": file_size,
            "duration_seconds": round(duration_sec, 2),
            "latency_ms": round(latency_ms, 1),
        }

    async def get_or_create_preview(self, voice_id: str) -> str:
        """
        Creates or retrieves an instant 3-second audio preview sample for voice cards.
        """
        preview_filename = f"prev_{voice_id}.mp3"
        preview_path = os.path.join(PREVIEWS_DIR, preview_filename)

        if not os.path.exists(preview_path):
            sample_text = "Hello! I am ready to give your content a professional voice."
            # Multilingual preview prompts
            if voice_id.startswith("hi-IN"):
                sample_text = "नमस्ते! मैं आपके प्रोजेक्ट के लिए एक आवाज़ देने के लिए तैयार हूँ।"
            elif voice_id.startswith("es-ES"):
                sample_text = "¡Hola! Estoy listo para darle voz profesional a tu contenido."
            elif voice_id.startswith("fr-FR"):
                sample_text = "Bonjour! Je suis prêt à donner vie à vos textes."
            elif voice_id.startswith("de-DE"):
                sample_text = "Hallo! Ich bin bereit, Ihren Texten eine professionelle Stimme zu geben."
            elif voice_id.startswith("ja-JP"):
                sample_text = "こんにちは！プロフェッショナルな音声をお届けします。"
            elif voice_id.startswith("zh-CN"):
                sample_text = "你好！我已经准备好为你的内容提供专业的声音。"

            comm = edge_tts.Communicate(text=sample_text, voice=voice_id)
            await comm.save(preview_path)

        return preview_filename

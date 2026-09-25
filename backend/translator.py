"""
VOX//PROTOCOL — Multilingual Neural Translation & Transliteration Engine
Implements zero-API-key cross-lingual translation with smart Romanized-Indic (Hinglish)
script detection and English-pivot normalization for authentic native vocoding.
"""

import json
import urllib.parse
import urllib.request
from typing import Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field

# Supported locale to 2-letter ISO translation code mapping
LOCALE_TO_TRANS_CODE = {
    "en-US": "en",
    "en-GB": "en",
    "en-IN": "en",
    "hi-IN": "hi",
    "es-ES": "es",
    "fr-FR": "fr",
    "de-DE": "de",
    "ja-JP": "ja",
    "zh-CN": "zh-CN",
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Mandarin": "zh-CN",
}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "zh-CN": "Chinese (Mandarin)",
}


class TranslationRequest(BaseModel):
    text: str = Field(..., max_length=5000, description="Input text to translate")
    target_lang: str = Field(..., description="Target language code or name (e.g. 'es', 'hi', 'Spanish')")
    source_lang: Optional[str] = Field("auto", description="Source language code (default: auto)")


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    source_lang_name: str
    target_lang: str
    target_lang_name: str
    is_romanized: bool
    pipeline: list


class TranslationEngine:
    def __init__(self):
        self._cache: Dict[Tuple[str, str], TranslationResponse] = {}

    def detect_script(self, text: str) -> str:
        """Determines predominant Unicode script."""
        if any("\u0900" <= c <= "\u097F" for c in text):
            return "Devanagari"
        if any("\u3040" <= c <= "\u30FF" or "\u31F0" <= c <= "\u31FF" for c in text):
            return "Japanese"
        if any("\u4E00" <= c <= "\u9FFF" for c in text):
            return "Chinese"
        return "Latin"

    def is_romanized_indic(self, text: str, detected_lang: str) -> bool:
        """
        Detects if text is Romanized Indic/Hinglish (Latin characters with Hindi semantics).
        """
        if self.detect_script(text) != "Latin":
            return False

        # Common phonetic tokens in Hinglish
        hinglish_tokens = {
            "mera", "meri", "mere", "naam", "hai", "hain", "kya", "kaisa", "kaise", "kaisi",
            "aap", "aapka", "aapki", "tum", "tumhara", "hum", "hamara", "bhai", "yaar",
            "achha", "accha", "theek", "shukriya", "dhanyawad", "dhanyavad", "namaste",
            "mujhe", "tumhe", "hoga", "hogi", "karo", "karna", "raha", "rahi", "rahe"
        }
        words = set(text.lower().replace(",", "").replace(".", "").split())
        if detected_lang == "hi":
            return True
        if words.intersection(hinglish_tokens):
            return True
        return False

    def normalize_target_code(self, target: str) -> str:
        """Converts locale or language name to standard ISO translation code."""
        if target in LOCALE_TO_TRANS_CODE:
            return LOCALE_TO_TRANS_CODE[target]
        for k, v in LOCALE_TO_TRANS_CODE.items():
            if target.lower() in k.lower():
                return v
        return target.lower()[:2]

    def _query_google_gtx(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, str]:
        """
        Queries high-speed neural translation gateway.
        """
        url = (
            f"https://translate.googleapis.com/translate_a/single?client=gtx"
            f"&sl={source_lang}&tl={target_lang}&dt=t&q=" + urllib.parse.quote(text)
        )
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=6.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated_parts = [part[0] for part in data[0] if part[0]]
            translated = "".join(translated_parts)
            detected = data[2] if len(data) > 2 else source_lang
            return translated.strip(), detected

    async def translate(self, req: TranslationRequest) -> TranslationResponse:
        """
        Executes cross-lingual translation with smart Romanized-Indic transliteration.
        """
        raw_text = req.text.strip()
        if not raw_text:
            return TranslationResponse(
                original_text=raw_text,
                translated_text=raw_text,
                source_lang="en",
                source_lang_name="English",
                target_lang=req.target_lang,
                target_lang_name=LANGUAGE_NAMES.get(req.target_lang, req.target_lang),
                is_romanized=False,
                pipeline=[]
            )

        target_code = self.normalize_target_code(req.target_lang)
        cache_key = (raw_text, target_code)
        if cache_key in self._cache:
            return self._cache[cache_key]

        pipeline = []

        try:
            # 1. Probe & Detect Source Language via English Pivot
            en_pivot, detected_lang = self._query_google_gtx(raw_text, source_lang="auto", target_lang="en")
            is_romanized = self.is_romanized_indic(raw_text, detected_lang)

            if is_romanized:
                pipeline.append("Romanized Indic (Hinglish) Detected")
                pipeline.append("Normalized to English Pivot")

            # 2. Case: Target is English
            if target_code == "en":
                translated_text = en_pivot
                pipeline.append("Direct to English")

            # 3. Case: Source was Romanized Hindi and Target is Hindi -> convert to Devanagari script
            elif is_romanized and target_code == "hi":
                # Translate English pivot to Hindi to get authentic Devanagari
                hi_text, _ = self._query_google_gtx(en_pivot, source_lang="en", target_lang="hi")
                translated_text = hi_text
                pipeline.append("Devanagari Script Synthesis")

            # 4. Case: Source is already native target language and not romanized
            elif detected_lang == target_code and not is_romanized:
                translated_text = raw_text
                pipeline.append("Source matches Target (No Translation needed)")

            # 5. Case: General Translation
            else:
                source_to_use = "en" if is_romanized else "auto"
                text_to_use = en_pivot if is_romanized else raw_text
                translated, _ = self._query_google_gtx(text_to_use, source_lang=source_to_use, target_lang=target_code)
                translated_text = translated
                pipeline.append(f"Translated to {LANGUAGE_NAMES.get(target_code, target_code)}")

            source_name = "Hindi (Romanized)" if is_romanized else LANGUAGE_NAMES.get(detected_lang, detected_lang.upper())
            target_name = LANGUAGE_NAMES.get(target_code, target_code.upper())

            response = TranslationResponse(
                original_text=raw_text,
                translated_text=translated_text,
                source_lang=detected_lang,
                source_lang_name=source_name,
                target_lang=target_code,
                target_lang_name=target_name,
                is_romanized=is_romanized,
                pipeline=pipeline
            )

            self._cache[cache_key] = response
            return response

        except Exception as e:
            # Resilient fallback: return original text with error pipeline note
            return TranslationResponse(
                original_text=raw_text,
                translated_text=raw_text,
                source_lang="unknown",
                source_lang_name="Original",
                target_lang=target_code,
                target_lang_name=LANGUAGE_NAMES.get(target_code, target_code),
                is_romanized=False,
                pipeline=[f"Fallback to Original (Notice: {str(e)})"]
            )

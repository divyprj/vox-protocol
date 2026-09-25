"""
VOX//PROTOCOL :  Multilingual Neural Translation & Transliteration Engine
Implements zero-API-key cross-lingual translation with resilient multi-gateway failover,
smart Romanized-Indic (Hinglish) transliteration, and high-availability caching.
"""

import json
import urllib.parse
import urllib.request
import re
from typing import Optional, Tuple, Dict, Any, List
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
        # In-memory translation cache to eliminate redundant network hits
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
            "mujhe", "tumhe", "hoga", "hogi", "karo", "karna", "raha", "rahi", "rahe",
            "nahi", "nhi", "bolo", "boliye", "kaun", "kab", "kaha", "kahan", "kyun", "kyu"
        }
        clean_words = set(re.sub(r"[^\w\s]", "", text.lower()).split())
        if detected_lang == "hi":
            return True
        if clean_words.intersection(hinglish_tokens):
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

    def _transliterate_indic_google(self, text: str) -> Optional[str]:
        """
        High-precision phonetic transliteration using Google Input Tools API.
        Specifically converts Romanized Hindi phonemes (Hinglish) into native Devanagari script.
        e.g. 'mera naam divyansh hai' -> 'मेरा नाम दिव्यांश है'
        """
        try:
            url = (
                "https://inputtools.google.com/request?text="
                + urllib.parse.quote(text)
                + "&itc=hi-t-i0-und&num=1&cp=0&cs=1&ie=utf-8&oe=utf-8&app=demopage"
            )
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data[0] == "SUCCESS" and len(data) > 1:
                    words = [item[1][0] for item in data[1] if item[1]]
                    if words:
                        return " ".join(words)
        except Exception:
            pass
        return None

    def _query_gateway_chrome(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, str]:
        """
        Tier 1: Google Chrome Extension Translation Gateway (High throughput, no 429 throttling).
        """
        url = (
            f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex"
            f"&sl={source_lang}&tl={target_lang}&q=" + urllib.parse.quote(text)
        )
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 0:
                first = data[0]
                if isinstance(first, list) and len(first) > 0:
                    translated = first[0]
                    detected = first[1] if len(first) > 1 else source_lang
                    return str(translated).strip(), str(detected)
                elif isinstance(first, str):
                    return first.strip(), source_lang
        raise ValueError("Invalid format from Chrome gateway")

    def _query_gateway_gtx(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, str]:
        """
        Tier 2: Google Translate GTX Single Gateway.
        """
        url = (
            f"https://translate.googleapis.com/translate_a/single?client=gtx"
            f"&sl={source_lang}&tl={target_lang}&dt=t&q=" + urllib.parse.quote(text)
        )
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated_parts = [part[0] for part in data[0] if part[0]]
            translated = "".join(translated_parts)
            detected = data[2] if len(data) > 2 else source_lang
            return translated.strip(), detected

    def _query_gateway_mymemory(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, str]:
        """
        Tier 3: MyMemory Translation API Gateway.
        """
        sl = "en" if source_lang == "auto" else source_lang
        url = (
            f"https://api.mymemory.translated.net/get?q="
            + urllib.parse.quote(text)
            + f"&langpair={sl}|{target_lang}"
        )
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated = data.get("responseData", {}).get("translatedText")
            if translated and translated.strip():
                return translated.strip(), sl
        raise ValueError("MyMemory empty response")

    def _translate_resilient(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, str]:
        """
        Attempts multi-gateway failover in order. Prevents any 429 rate limit errors from failing synthesis.
        """
        gateways = [
            ("Chrome Extension", self._query_gateway_chrome),
            ("Google GTX", self._query_gateway_gtx),
            ("MyMemory", self._query_gateway_mymemory),
        ]

        last_error = None
        for name, gateway in gateways:
            try:
                translated, detected = gateway(text, source_lang, target_lang)
                if translated and translated.strip():
                    return translated, detected
            except Exception as e:
                last_error = e
                continue

        # If all fail, return original
        return text, source_lang

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
        cache_key = (raw_text.lower(), target_code)
        if cache_key in self._cache:
            return self._cache[cache_key]

        pipeline = []

        try:
            # 1. Probe & Detect Source Language via English Pivot
            en_pivot, detected_lang = self._translate_resilient(raw_text, source_lang="auto", target_lang="en")
            is_romanized = self.is_romanized_indic(raw_text, detected_lang)

            if is_romanized:
                pipeline.append("Romanized Indic (Hinglish) Detected")

            # 2. Case: Romanized Hindi -> Devanagari Hindi
            if is_romanized and target_code == "hi":
                # Try direct high-precision phonetic transliteration first
                translit_res = self._transliterate_indic_google(raw_text)
                if translit_res:
                    translated_text = translit_res
                    pipeline.append("Phonetic Devanagari Transliteration")
                else:
                    # Fallback to English pivot -> Devanagari translation
                    hi_text, _ = self._translate_resilient(en_pivot, source_lang="en", target_lang="hi")
                    translated_text = hi_text
                    pipeline.append("Devanagari Script Synthesis")

            # 3. Case: Romanized Hindi -> Other Language (e.g. Spanish, French)
            elif is_romanized and target_code != "hi":
                if target_code == "en":
                    translated_text = en_pivot
                    pipeline.append("Hinglish Normalized to English")
                else:
                    translated, _ = self._translate_resilient(en_pivot, source_lang="en", target_lang=target_code)
                    translated_text = translated
                    pipeline.append(f"Translated to {LANGUAGE_NAMES.get(target_code, target_code)}")

            # 4. Case: Source matches Target (and not romanized)
            elif detected_lang == target_code and not is_romanized:
                translated_text = raw_text
                pipeline.append("Source matches Target Language")

            # 5. Case: General Translation
            else:
                translated, _ = self._translate_resilient(raw_text, source_lang="auto", target_lang=target_code)
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

            # Prevent memory overflow: limit cache to 500 items
            if len(self._cache) > 500:
                self._cache.clear()
            self._cache[cache_key] = response
            return response

        except Exception as e:
            # Resilient fallback: return original text with user-friendly note
            return TranslationResponse(
                original_text=raw_text,
                translated_text=raw_text,
                source_lang="unknown",
                source_lang_name="Original",
                target_lang=target_code,
                target_lang_name=LANGUAGE_NAMES.get(target_code, target_code),
                is_romanized=False,
                pipeline=["Native Script Preserved"]
            )

"""
Verification Test Suite for VOX//PROTOCOL
Runs asynchronous HTTP calls against all endpoints:
Voices, Speech Generation (English & Hindi, Male & Female), History, Previews, Analytics, and Benchmark.
"""

import sys
import os
import asyncio
import httpx

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.main import app
from backend.database import init_db

async def run_suite():
    init_db()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        print("\n--- 0. Testing Cloud Health Telemetry (/api/health) ---")
        health_res = await client.get("/api/health")
        assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
        h_data = health_res.json()
        print(f"Health check OK: {h_data['status']} | service: {h_data['service']} | v{h_data['version']}")
        assert h_data["status"] == "healthy"

        print("\n--- 1. Testing Voice Catalog (/api/voices) ---")
        res = await client.get("/api/voices")
        assert res.status_code == 200, f"Failed: {res.text}"
        voices = res.json()
        print(f"Loaded {len(voices)} studio voices.")
        
        languages = set(v["language"] for v in voices)
        genders = set(v["gender"] for v in voices)
        print(f"Supported Languages: {sorted(list(languages))}")
        print(f"Genders: {sorted(list(genders))}")
        assert "English" in languages and "Hindi" in languages, "Missing target languages!"
        assert "Female" in genders and "Male" in genders, "Missing male/female diversity!"
        
        print("\n--- 2. Testing Voice Preview (/api/preview/{voice_id}) ---")
        prev_res = await client.get("/api/preview/en-US-JennyNeural")
        assert prev_res.status_code == 200, f"Preview failed: {prev_res.text}"
        assert len(prev_res.content) > 1000, "Preview audio too small!"
        print(f"Preview generated successfully! Size: {len(prev_res.content)} bytes.")

        print("\n--- 3. Testing Speech Synthesis - English Female (/api/generate) ---")
        gen_en = await client.post("/api/generate", json={
            "text": "Hello and welcome to VOX Protocol. High quality neural speech synthesis is now active.",
            "voice_id": "en-US-JennyNeural",
            "speed": 1.0,
            "pitch": 0,
            "volume": 100
        })
        assert gen_en.status_code == 200, f"EN Generation failed: {gen_en.text}"
        en_data = gen_en.json()
        print(f"Synthesized EN audio: ID={en_data['id']}, Duration={en_data['duration_seconds']}s, Latency={en_data['latency_ms']}ms")
        assert os.path.exists(os.path.join("output", f"{en_data['id']}.mp3")), "Output file does not exist!"

        print("\n--- 4. Testing Speech Synthesis - Hindi Male (/api/generate) ---")
        gen_hi = await client.post("/api/generate", json={
            "text": "नमस्ते! वॉक्स प्रोटोकॉल में आपका स्वागत है।",
            "voice_id": "hi-IN-MadhurNeural",
            "speed": 1.0,
            "pitch": 0,
            "volume": 100
        })
        assert gen_hi.status_code == 200, f"HI Generation failed: {gen_hi.text}"
        hi_data = gen_hi.json()
        print(f"Synthesized HI audio: ID={hi_data['id']}, Duration={hi_data['duration_seconds']}s, Latency={hi_data['latency_ms']}ms")
        assert os.path.exists(os.path.join("output", f"{hi_data['id']}.mp3")), "Output file does not exist!"

        print("\n--- 5. Testing Generation History (/api/history) ---")
        hist_res = await client.get("/api/history")
        assert hist_res.status_code == 200
        hist = hist_res.json()
        print(f"History retrieved {len(hist)} items.")
        assert len(hist) >= 2, "Expected at least 2 history items!"

        print("\n--- 6. Testing Telemetry Analytics (/api/analytics) ---")
        an_res = await client.get("/api/analytics")
        assert an_res.status_code == 200
        analytics = an_res.json()
        print(f"Platform Analytics: Generations={analytics['total_generations']}, Mean RTF={analytics['mean_rtf']}x, Speedup={analytics['realtime_speedup']}x")

        print("\n--- 7. Testing Automated Benchmark (/api/benchmark) ---")
        bench_res = await client.post("/api/benchmark?sample_count=3")
        assert bench_res.status_code == 200, f"Benchmark failed: {bench_res.text}"
        bench = bench_res.json()
        print(f"Benchmark Results: Samples={bench['sample_count']}, Global RTF={bench['global_rtf']}x, Speedup={bench['realtime_speedup']}x, Throughput={bench['character_throughput_per_sec']} chars/s")

        print("\n--- 8. Testing History Item Deletion (/api/history/{id}) ---")
        del_res = await client.delete(f"/api/history/{hi_data['id']}")
        assert del_res.status_code == 200
        print(f"Successfully deleted {hi_data['id']}.")

        print("\n--- 9. Testing Multilingual Neural Translation & Transliteration (/api/translate) ---")
        # Test 9A: Romanized Hindi to Spanish
        tr_es = await client.post("/api/translate", json={
            "text": "mera naam divyansh hai",
            "target_lang": "es"
        })
        assert tr_es.status_code == 200, f"Translation failed: {tr_es.text}"
        data_es = tr_es.json()
        print(f"[Hinglish -> Spanish]: '{data_es['original_text']}' ==> '{data_es['translated_text']}' (Source: {data_es['source_lang_name']})")
        assert "divyansh" in data_es['translated_text'].lower(), "Expected translated text to preserve name!"

        # Test 9B: Romanized Hindi to Devanagari Hindi
        tr_hi = await client.post("/api/translate", json={
            "text": "mera naam divyansh hai",
            "target_lang": "hi"
        })
        assert tr_hi.status_code == 200
        data_hi = tr_hi.json()
        print(f"[Hinglish -> Devanagari Hindi]: '{data_hi['original_text']}' ==> '{data_hi['translated_text']}' (Pipeline: {data_hi['pipeline']})")
        assert any("\u0900" <= c <= "\u097F" for c in data_hi['translated_text']), "Expected Devanagari script!"

        # Test 9C: English to French
        tr_fr = await client.post("/api/translate", json={
            "text": "Welcome to our voice AI studio",
            "target_lang": "fr"
        })
        assert tr_fr.status_code == 200
        data_fr = tr_fr.json()
        print(f"[English -> French]: '{data_fr['original_text']}' ==> '{data_fr['translated_text']}'")

        print("\n==============================================")
        print("ALL VOX//PROTOCOL TEST SUITES PASSED (100% OK)")
        print("==============================================")

if __name__ == "__main__":
    asyncio.run(run_suite())

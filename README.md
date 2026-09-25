# VOX//PROTOCOL: High-Fidelity Multilingual Neural Voice Studio

VOX//PROTOCOL is a production-oriented multilingual Text-to-Speech platform designed for high-quality neural speech generation, multilingual voice workflows, audio experimentation, and measurable synthesis performance.

The platform provides a polished browser-based voice workstation with 49 curated neural voices, automatic multilingual translation, Romanized Indic transliteration, real-time acoustic controls, persistent generation history, interactive audio visualization, and an integrated benchmarking system.

VOX//PROTOCOL requires no paid API credentials, no dedicated GPU, and no local neural inference hardware. Neural speech synthesis is performed through the Microsoft Edge neural speech infrastructure using a zero-key integration.

---

## Live Platform

- **Production Application**: [https://vox-protocol.onrender.com](https://vox-protocol.onrender.com)
- **Interactive OpenAPI Documentation**: [https://vox-protocol.onrender.com/docs](https://vox-protocol.onrender.com/docs)
- **GitHub Repository**: [https://github.com/divyprj/vox-protocol](https://github.com/divyprj/vox-protocol)

---

## Platform Overview

VOX//PROTOCOL provides a unified neural voice workstation for converting written content into natural multilingual speech.

The system combines:

- Multilingual neural Text-to-Speech synthesis
- Male and female voice selection across all locales
- Automatic language-aware translation
- Romanized Indic (Hinglish) transliteration
- Real-time acoustic parameter controls (Rate, Pitch, Volume)
- Instant voice preview auditioning
- Interactive canvas waveform playback
- Persistent local generation history
- MP3 audio export
- Performance telemetry
- Automated benchmarking suite
- REST API access through FastAPI
- One-click Windows execution (`start.bat` / `stop.bat`)
- Docker-based container deployment

The platform is designed to support both direct interactive use and programmatic integration through its REST API.

---

## Core Capabilities

### Multilingual Neural Speech

VOX//PROTOCOL exposes 49 curated studio-quality neural voices across seven major languages and nine supported locale groups.

Supported language coverage includes:

| Language | Locales |
| :--- | :--- |
| English | United States (en-US), United Kingdom (en-GB), India (en-IN) |
| Hindi | India (hi-IN) |
| Spanish | Spain (es-ES) |
| French | France (fr-FR) |
| German | Germany (de-DE) |
| Japanese | Japan (ja-JP) |
| Mandarin Chinese | Mainland China (zh-CN) |

The voice catalog includes balanced male and female representation, allowing users to select voice identity independently from language.

Voice metadata includes:
- Display name
- Locale
- Language
- Gender
- Voice identifier
- Preview availability

---

### Instant Voice Auditioning

Each supported voice can be auditioned through a short native-language preview. The preview system allows users to compare voices before generating a complete audio file.

Typical workflow:

```text
Select language
    |
    v
Filter by gender
    |
    v
Preview voice (3s native tongue sample)
    |
    v
Select preferred voice
    |
    v
Generate final speech
```

Preview audio is cached locally to minimize repeated network requests and reduce perceived latency.

---

### Automatic Translation

VOX//PROTOCOL can automatically translate source text into the native language associated with the selected target voice.

Example:

- Input: `mera naam divyansh hai`
- Hindi voice: `मेरा नाम दिव्यांश है`
- English voice: `My name is Divyansh.`
- Spanish voice: `Mi nombre es Divyansh.`

The original source text remains preserved while the translated speech representation is generated separately. This architecture allows users to switch between languages without rewriting the source script.

---

### Romanized Indic Transliteration

The platform includes a dedicated Romanized Indic processing path for text written phonetically in Latin characters.

Example:
- Romanized Hindi: `mera naam divyansh hai`
- Native Hindi: `मेरा नाम दिव्यांश है`

This allows users to write Hindi naturally using a standard Latin keyboard while still generating correctly scripted Hindi speech.

The translation pipeline separates:

```text
Language Detection
        |
        v
Script Detection
        |
        v
Romanized Indic Transliteration
        |
        v
Translation
        |
        v
Speech Synthesis
```

Transliteration and translation are intentionally treated as separate operations.

---

### Acoustic Controls

VOX//PROTOCOL exposes configurable speech parameters directly from the Studio interface.

#### Speech Rate
- Supported range: `0.5x` to `2.0x`
- Supports slow instructional delivery, standard conversational delivery, and fast technical narration.

#### Pitch
- Supported range: `-50 Hz` to `+50 Hz`
- Pitch adjustment can be applied without changing the selected voice identity.

#### Volume
- Output gain can be adjusted directly before generation (`0%` to `100%`).

These controls are applied as part of the synthesis configuration and are preserved in the generation metadata.

---

### Studio Workstation

The Studio is the primary interface for content creation. It includes:

- Large script editor with 5,000-character capacity
- Character and word counter
- Language selection pills
- Voice browser with text search
- Male and female gender filters
- Instant voice previews
- Speech rate, pitch, and volume controls
- Automatic translation controls with interactive preview card
- Script presets (Narrative, Commercial, Assistant, Technical Explainer)
- Interactive waveform player

The interface uses a restrained dark workstation design optimized for long-duration use and high information density.

---

### Interactive Audio Player

Generated speech is presented through a custom audio playback interface. Capabilities include:

- Play and Pause
- Timeline seeking and scrubbing
- Real-time HTML5 Canvas waveform visualization
- Current playback time and total duration display
- Audio replay
- High-fidelity MP3 download
- Source text copy

Waveform rendering is performed directly through the HTML5 Canvas API at 60 frames per second.

---

### Persistent Audio Library

Every generated audio asset can be persisted locally. The Library provides:

- Full generation history
- Source text and spoken text tracking
- Selected language, voice, and gender metadata
- Generation timestamp
- Audio duration
- Direct playback and MP3 download
- Granular record deletion

Metadata is stored using SQLite with indexed timestamp ordering. Generated audio remains associated with its original synthesis configuration, allowing historical results to be reproduced and inspected.

---

### Benchmarking and Telemetry

VOX//PROTOCOL includes an automated performance benchmark suite designed to measure speech synthesis efficiency across configurable test sets.

The benchmark runner supports controlled test batches, including 5, 10, 20, and 50 to 100 sample workloads.

Measured telemetry includes:

- **Generation Latency (`generation_latency_ms`)**: Wall-clock time required to complete a synthesis request.
- **Real-Time Factor (RTF)**: Ratio of synthesis time to generated audio duration:
  $$\text{RTF} = \frac{\text{generation\_time}}{\text{generated\_audio\_duration}}$$
  An RTF of 0.20 means that five seconds of audio requires approximately one second of synthesis time. Lower values indicate higher synthesis efficiency.
- **Real-Time Speedup**: Real-time generation multiplier:
  $$\text{Speedup} = \frac{\text{generated\_audio\_duration}}{\text{generation\_time}}$$
- **Character Throughput**: Characters converted per second:
  $$\text{Throughput} = \frac{\text{input\_character\_count}}{\text{generation\_time}}$$

---

### Verified Performance

Observed verification runs have demonstrated the following operating range:

| Metric | Observed Result |
| :--- | :--- |
| End-to-end generation latency | Under 900 ms for typical short-form inputs |
| Real-Time Factor (RTF) | Approximately 0.18 to 0.24 |
| Real-time speedup | Greater than 4x faster than real time |
| API credential requirement | None (Zero-key architecture) |
| GPU requirement | None (Runs on any standard CPU) |
| Test suite status | 100% passing across all 10 system checkpoints |

Because speech synthesis is performed through the Microsoft Edge neural speech service, reported generation latency represents end-to-end application latency rather than isolated local model inference time.

---

## System Architecture

```text
                         VOX//PROTOCOL
                               |
                               v
                    +----------------------+
                    |   Browser Workstation|
                    |                      |
                    |  HTML5               |
                    |  Vanilla JavaScript  |
                    |  Canvas Waveform     |
                    +----------+-----------+
                               |
                               | HTTPS / JSON
                               v
                    +----------------------+
                    |    FastAPI ASGI Core |
                    |                      |
                    |  Request Validation  |
                    |  Voice Management    |
                    |  Translation         |
                    |  Generation          |
                    |  History             |
                    |  Analytics           |
                    |  Benchmarking        |
                    +-----+-----------+----+
                          |           |
             +------------+           +----------------+
             |                                         |
             v                                         v
    +----------------------+                  +------------------+
    | Language Pipeline    |                  | SQLite Storage   |
    |                      |                  |                  |
    | Language Detection   |                  | Generations      |
    | Script Detection     |                  | Voice Metadata   |
    | Transliteration      |                  | Telemetry        |
    | Translation          |                  | History          |
    +----------+-----------+                  +---------+--------+
               |                                        |
               v                                        |
    +----------------------+                            |
    | Neural TTS Provider  |                            |
    |                      |                            |
    | Microsoft Edge       |                            |
    | Neural Speech Engine |                            |
    +----------+-----------+                            |
               |                                        |
               v                                        |
    +----------------------+                            |
    | Audio Processing     |                            |
    |                      |                            |
    | MP3 Generation       |                            |
    | Duration Analysis    |                            |
    | Audio Metadata       |                            |
    +----------+-----------+                            |
               |                                        |
               +--------------------+-------------------+
                                    |
                                    v
                         +----------------------+
                         | Generated Audio Store|
                         |                      |
                         | MP3 Assets           |
                         | Preview Cache        |
                         +----------------------+
```

---

## REST API Reference

FastAPI exposes a typed REST interface for voice discovery, synthesis, translation, history, analytics, and benchmarking.

Interactive API documentation is available at:
`https://vox-protocol.onrender.com/docs`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Returns service health and runtime telemetry |
| `GET` | `/api/voices` | Returns the complete curated neural voice catalog |
| `GET` | `/api/preview/{id}` | Streams an instant 3-second preview audio sample |
| `POST` | `/api/translate` | Translates or transliterates input text for a target voice |
| `POST` | `/api/generate` | Generates high-fidelity neural speech from text |
| `GET` | `/api/history` | Returns persisted generation history with playable URLs |
| `DELETE` | `/api/history/{id}` | Deletes a stored generation record and audio file |
| `GET` | `/api/analytics` | Returns platform latency, RTF, speedup, and throughput |
| `POST` | `/api/benchmark` | Executes automated multi-prompt benchmark sweeps |

### API Request Examples

#### Health Telemetry
```http
GET /api/health HTTP/1.1
```
Response:
```json
{
  "status": "healthy",
  "service": "VOX//PROTOCOL Neural Voice Studio",
  "version": "2.1.0",
  "timestamp": "2026-09-25T10:00:00Z"
}
```

#### Speech Generation
```http
POST /api/generate HTTP/1.1
Content-Type: application/json

{
  "text": "VOX Protocol converts multilingual text into natural neural speech.",
  "voice_id": "en-US-JennyNeural",
  "speed": 1.0,
  "pitch": 0,
  "volume": 100
}
```
Response:
```json
{
  "id": "vox_84ba898d56",
  "text": "VOX Protocol converts multilingual text into natural neural speech.",
  "voice_id": "en-US-JennyNeural",
  "voice_name": "Jenny",
  "gender": "Female",
  "language": "English",
  "audio_url": "/output/vox_84ba898d56.mp3",
  "duration_seconds": 4.82,
  "file_size_bytes": 29480,
  "latency_ms": 877.8,
  "created_at": "2026-09-25T10:00:05Z"
}
```

#### Cross-Lingual Translation & Transliteration
```http
POST /api/translate HTTP/1.1
Content-Type: application/json

{
  "text": "mera naam divyansh hai",
  "target_lang": "es"
}
```
Response:
```json
{
  "original_text": "mera naam divyansh hai",
  "translated_text": "mi nombre es divyansh",
  "source_lang": "hi",
  "source_lang_name": "Hindi (Romanized)",
  "target_lang": "es",
  "target_lang_name": "Spanish",
  "is_romanized": true,
  "pipeline": [
    "Romanized Indic (Hinglish) Detected",
    "Translated to Spanish"
  ]
}
```

---

## Quickstart Guide

### Option 1: Windows One-Click Launch

1. Clone the repository:
```cmd
git clone https://github.com/divyprj/vox-protocol.git
cd vox-protocol
```

2. Start the platform:
```cmd
start.bat
```
The launcher initializes dependencies, starts the FastAPI server, and opens `http://localhost:8000` automatically.

3. Stop the platform cleanly:
```cmd
stop.bat
```

### Option 2: Docker and Docker Compose

1. Clone and enter the repository:
```bash
git clone https://github.com/divyprj/vox-protocol.git
cd vox-protocol
```

2. Start with Docker Compose:
```bash
docker compose up -d
```
Access the studio at `http://localhost:8000`.

3. Stop:
```bash
docker compose down
```

### Option 3: Manual Python Execution

Requirements:
- Python 3.11+
- Internet connectivity for neural speech generation

1. Setup environment:
```bash
git clone https://github.com/divyprj/vox-protocol.git
cd vox-protocol
python -m venv .venv
```

2. Activate virtual environment:
- Windows:
```cmd
.venv\Scripts\activate
```
- Linux / macOS:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Launch server:
```bash
python run_server.py
```
Open `http://localhost:8000` in your web browser.

---

## Verification & Automated Testing

Run the full end-to-end automated test suite:

```powershell
python test_vox.py
```

Tested checkpoints:
1. Cloud health telemetry (`/api/health`)
2. Studio voice catalog discovery (49 curated voices across 7 languages)
3. Instant voice preview MP3 generation
4. Multilingual synthesis for English Female (`Jenny`) and Hindi Male (`Madhur`)
5. SQLite generation persistence and retrieval
6. Telemetry calculation (Latency, RTF, Speedup)
7. Automated multi-prompt benchmark sweep
8. Deletion and cleanup routines
9. Romanized Indic (Hinglish) transliteration & multi-language translation pipeline

---

## Technical Specifications

| Component | Technology |
| :--- | :--- |
| Runtime | Python 3.11 |
| Backend Framework | FastAPI (ASGI) |
| Web Server | Uvicorn |
| Neural Speech Layer | Microsoft Edge Neural Speech Core |
| TTS Integration | edge-tts (Asynchronous WebSocket) |
| Database | SQLite3 with Indexed Timestamp Ordering |
| Frontend | HTML5, Vanilla JavaScript |
| Waveform Rendering | HTML5 Canvas API (60 FPS) |
| API Standard | OpenAPI 3.0 (Swagger UI) |
| Audio Codec | MPEG Layer-3 (MP3), 24kHz / 48kbps mono voice profile |
| Container Runtime | Docker, Docker Compose |
| Cloud Deployment | Render (Web Service), Railway |

---

## Author

**Divyansh**
- GitHub: [divyprj](https://github.com/divyprj)
- Repository: [github.com/divyprj/vox-protocol](https://github.com/divyprj/vox-protocol)
- Email: surajdivyansh104@gmail.com
- License: MIT

"""
VOX//PROTOCOL :  Neural Voice Studio
Production SaaS Server Launcher
"""

import os
import sys
import time
import threading
import webbrowser
import uvicorn

PORT = int(os.environ.get("PORT", 8000))
# If PORT is set (cloud hosting like Render/Railway), bind to 0.0.0.0; otherwise 127.0.0.1 locally
DEFAULT_HOST = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
HOST = os.environ.get("HOST", DEFAULT_HOST)
URL = f"http://{'localhost' if HOST == '0.0.0.0' else HOST}:{PORT}"
IS_CLOUD = bool(os.environ.get("PORT") or os.environ.get("RENDER") or os.environ.get("RAILWAY_STATIC_URL"))


def open_browser():
    if IS_CLOUD or os.environ.get("HEADLESS"):
        return
    time.sleep(1.2)
    print(f"\n[VOX//PROTOCOL] Opening interactive studio in browser: {URL}\n")
    try:
        webbrowser.open(URL)
    except Exception:
        pass


def main():
    print("=" * 64)
    print("  VOX//PROTOCOL :  NEURAL VOICE STUDIO (v2.1.0)")
    print("  Enterprise Text-to-Speech & Voice AI Platform")
    print("=" * 64)
    print(f"  • Engine: Edge Neural Voice Core (320+ Studio Voices)")
    print(f"  • Multilingual: English, Hindi, Spanish, French, German, Japanese, Chinese")
    print(f"  • Host: {HOST}")
    print(f"  • Port: {PORT}")
    print(f"  • Dashboard: {URL}")
    print(f"  • Interactive API Docs: {URL}/docs")
    print(f"  • Health Check: {URL}/api/health")
    print("=" * 64)

    # Launch browser automatically in background for desktop mode
    if not IS_CLOUD and not os.environ.get("HEADLESS"):
        threading.Thread(target=open_browser, daemon=True).start()

    # Start Uvicorn ASGI server
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        log_level="info",
        reload=False
    )


if __name__ == "__main__":
    main()

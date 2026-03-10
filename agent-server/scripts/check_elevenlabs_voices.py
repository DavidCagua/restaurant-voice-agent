#!/usr/bin/env python3
"""
Diagnose ElevenLabs voices and subscription.
Run from repo root: python agent-server/scripts/check_elevenlabs_voices.py
Or from agent-server: python scripts/check_elevenlabs_voices.py

Uses ELEVEN_API_KEY from .env (project root or agent-server).
"""
import json
import os
import sys
from pathlib import Path

# Load .env from project root or agent-server
root = Path(__file__).resolve().parents[2]
env_path = root / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))

API_KEY = os.environ.get("ELEVEN_API_KEY")
if not API_KEY:
    print("ERROR: ELEVEN_API_KEY not set in .env")
    sys.exit(1)

BASE = "https://api.elevenlabs.io/v1"
HEADERS = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

def get(path: str) -> dict:
    import urllib.request
    req = urllib.request.Request(f"{BASE}{path}", headers=HEADERS, method="GET")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def get_raw(path: str) -> tuple[int, bytes]:
    import urllib.request
    req = urllib.request.Request(f"{BASE}{path}", headers=HEADERS, method="GET")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

def post_tts(voice_id: str, text: str) -> tuple[int, bytes]:
    import urllib.request
    url = f"{BASE}/text-to-speech/{voice_id}"
    body = json.dumps({"text": text, "model_id": "eleven_turbo_v2_5"}).encode()
    req = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

def main():
    print("=== 1. Your subscription (tier limits Voice Library API access) ===\n")
    try:
        sub = get("/user/subscription")
        print(f"  tier: {sub.get('tier', '?')}")
        print(f"  character_count: {sub.get('character_count')} / {sub.get('character_limit')}")
        print(f"  voice_limit: {sub.get('voice_limit')}")
    except Exception as e:
        print(f"  Failed: {e}\n")

    print("\n=== 2. Voices available via API (GET /v1/voices) ===\n")
    try:
        data = get("/voices")
        voices = data.get("voices", [])
        for v in voices:
            print(f"  id: {v.get('voice_id')}  name: {v.get('name')}  category: {v.get('category')}")
        if not voices:
            print("  (none)")
    except Exception as e:
        print(f"  Failed: {e}\n")

    # Colombian voice ID you tried
    colombian_id = "86V9x9hrQds83qf7zaGn"
    print(f"\n=== 3. TTS test with voice_id={colombian_id} (Colombian) ===\n")
    try:
        status, body = post_tts(colombian_id, "Hola, el menú por favor.")
        print(f"  HTTP status: {status}")
        if len(body) < 500:
            print(f"  body: {body.decode(errors='replace')}")
        else:
            print(f"  body (first 500 chars): {body[:500].decode(errors='replace')}...")
    except Exception as e:
        print(f"  Failed: {e}")

    print("\n=== Note ===\n")
    print("  ElevenLabs docs: 'The voice library is not available via the API to free tier users.'")
    print("  If your tier is 'free' and the Colombian voice is from Voice Library, it will not work via API.")
    print("  Use a default voice (e.g. rola) or upgrade to use Voice Library voices via API.")

if __name__ == "__main__":
    main()

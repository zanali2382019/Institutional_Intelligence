"""
Institutional Intelligence Studio — Google Chirp3-HD Charon Voice Generator
Voice: ar-XA-Chirp3-HD-Charon (Google Cloud / Gemini Chirp 3 HD Architecture)
Generates studio broadcast Arabic audio using Google Text-to-Speech API.
"""

import os
import sys
import json
import base64
import argparse
import requests
from pathlib import Path

# Fix console encodings on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VOICE_NAME = "ar-XA-Chirp3-HD-Charon"
LANGUAGE_CODE = "ar-XA"

def synthesize_text(text: str, out_path: str, api_key: str = None, rate: float = 1.04):
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GCP_API_KEY")
    
    if not key:
        print("[!] Error: No API key found.")
        print("[!] Please provide an API key via --api-key or set the GEMINI_API_KEY / GOOGLE_API_KEY environment variable.")
        print("[!] You can obtain a key at: https://aistudio.google.com/apikey or Google Cloud Console.")
        sys.exit(1)

    url = f"https://texttospeech.googleapis.com/v1beta1/text:synthesize?key={key}"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    payload = {
        "input": {"text": text},
        "voice": {
            "languageCode": LANGUAGE_CODE,
            "name": VOICE_NAME
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": rate
        }
    }

    print(f"[*] Calling Google Cloud Text-to-Speech API...")
    print(f"[*] Voice: {VOICE_NAME} | Rate: {rate}x")

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if resp.status_code != 200:
        print(f"[!] API Error ({resp.status_code}): {resp.text}")
        # Try v1 fallback
        url_v1 = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={key}"
        resp_v1 = requests.post(url_v1, headers=headers, json=payload, timeout=60)
        if resp_v1.status_code == 200:
            resp = resp_v1
        else:
            sys.exit(1)

    data = resp.json()
    audio_content = data.get("audioContent")
    if not audio_content:
        print(f"[!] No audioContent in response: {data}")
        sys.exit(1)

    audio_bytes = base64.b64decode(audio_content)
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(audio_bytes)
    print(f"[OK] Audio successfully generated with voice {VOICE_NAME}!")
    print(f"[OK] Saved to: {out_path} ({len(audio_bytes) / 1024:.1f} KB)")

def main():
    parser = argparse.ArgumentParser(description="Synthesize Arabic voiceover with ar-XA-Chirp3-HD-Charon")
    parser.add_argument("--text", type=str, required=True, help="Text string or path to .txt file")
    parser.add_argument("--out", type=str, required=True, help="Output mp3 file path")
    parser.add_argument("--api-key", type=str, default=None, help="Google API key")
    parser.add_argument("--rate", type=float, default=1.04, help="Speaking rate (default: 1.04)")
    args = parser.parse_args()

    content = args.text
    if os.path.exists(args.text):
        content = Path(args.text).read_text(encoding="utf-8")

    synthesize_text(content, args.out, args.api_key, args.rate)

if __name__ == '__main__':
    main()


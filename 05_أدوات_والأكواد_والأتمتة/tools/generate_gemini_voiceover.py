"""
Institutional Intelligence Studio — Gemini TTS Voiceover Generator
Uses Google Gemini API (gemini-3.8-flash-tts) for studio-grade voiceover.
Top clear voices:
  - Iapetus (Clear - الأعلى وضوحاً ونقاءً)
  - Charon (Informative - إخباري ورزين)
  - Sadaltager (Knowledgeable - معرفي وشرح تقني)
  - Orus (Firm - حازم وتنفيذي)
  - Kore (Firm - واثق ومؤسسي)
"""

import os
import sys
import argparse
import base64
from pathlib import Path

# Fix console encodings on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GEMINI_CLEAR_VOICES = {
    'iapetus': 'Iapetus',       # Clear (الأعلى نقاءً ووضوحاً)
    'charon': 'Charon',         # Informative (إخباري ورزين)
    'sadaltager': 'Sadaltager', # Knowledgeable (معرفي وشرح تقني متقدم)
    'orus': 'Orus',             # Firm (تنفيذي وحازم)
    'kore': 'Kore',             # Firm (واثق ومؤسسي)
}

def generate_with_gemini(text: str, voice_name: str, out_path: str, api_key: str = None):
    try:
        from google import genai
    except ImportError:
        print("[!] google-genai is not installed. Please install it using: pip install google-genai")
        sys.exit(1)

    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        print("[!] Error: No GEMINI_API_KEY provided.")
        print("[!] Please set GEMINI_API_KEY environment variable or pass --api-key.")
        print("[!] You can get a free API key instantly at: https://aistudio.google.com/apikey")
        sys.exit(1)

    print(f"[*] Initializing Gemini Client with voice: {voice_name}...")
    client = genai.Client(api_key=key, http_options={"api_version": "v1beta"})

    selected_voice = GEMINI_CLEAR_VOICES.get(voice_name.lower(), voice_name)
    print(f"[*] Generating speech using Gemini TTS (Voice: {selected_voice})...")

    # Split text if very large, or generate directly
    try:
        interaction = client.interactions.create(
            model="gemini-3.8-flash-tts",
            input=[{
                "type": "user_input",
                "content": [{
                    "type": "text",
                    "text": text,
                    "annotations": [{
                        "type": "speech_metadata",
                        "style": "crystal clear, articulate, authoritative and professional Arabic executive delivery",
                    }],
                }],
            }],
            response_format={"type": "audio"},
            generation_config={
                "speech_config": [
                    {"voice": selected_voice},
                ]
            },
        )

        audio_bytes = None
        if hasattr(interaction, 'output_audio') and interaction.output_audio and hasattr(interaction.output_audio, 'data'):
            audio_bytes = base64.b64decode(interaction.output_audio.data)
        elif hasattr(interaction, 'steps'):
            for step in interaction.steps:
                if getattr(step, 'type', None) == 'model_output':
                    for c in getattr(step, 'content', []):
                        if getattr(c, 'type', None) == 'audio':
                            audio_bytes = base64.b64decode(c.data)
                            break

        if not audio_bytes:
            raise RuntimeError("No audio data returned by Gemini API")

        out_file = Path(out_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_bytes(audio_bytes)
        print(f"[OK] Gemini Voiceover successfully saved to: {out_path} ({len(audio_bytes) / 1024:.1f} KB)")

    except Exception as e:
        print(f"[!] Gemini TTS Generation failed: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Generate Executive Voiceover using Google Gemini TTS")
    parser.add_argument("--text", type=str, required=True, help="Text to speak or path to .txt file")
    parser.add_argument("--voice", type=str, default="iapetus", choices=list(GEMINI_CLEAR_VOICES.keys()) + list(GEMINI_CLEAR_VOICES.values()), help="Gemini clear voice option")
    parser.add_argument("--out", type=str, required=True, help="Output audio file path (.wav or .mp3)")
    parser.add_argument("--api-key", type=str, default=None, help="Gemini API Key")
    args = parser.parse_args()

    content = args.text
    if os.path.exists(args.text):
        content = Path(args.text).read_text(encoding="utf-8")

    generate_with_gemini(content, args.voice, args.out, args.api_key)

if __name__ == '__main__':
    main()


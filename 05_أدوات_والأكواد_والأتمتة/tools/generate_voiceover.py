"""
Institutional Intelligence Studio — AI Voiceover Generator
Uses Microsoft Azure Neural TTS (Edge-TTS) for free broadcast-quality Arabic executive voiceover.
Default voice: ar-SA-HamedNeural (Saudi authoritative male executive).
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
import edge_tts

# Fix console encodings on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VOICE_OPTIONS = {
    'saudi_male': 'ar-SA-HamedNeural',       # رصين إخباري وتنفيذي (المفضل للذكاء المؤسسي)
    'saudi_female': 'ar-SA-ZariyahNeural',   # نسائي فصيح هادئ وواثق
    'uae_male': 'ar-AE-HamdanNeural',        # إماراتي حديث ومناسب للتقنية
    'egypt_male': 'ar-EG-ShakirNeural',      # مصري إخباري فصيح
}

async def generate(text: str, voice_key: str, out_path: str, rate: str):
    voice = VOICE_OPTIONS.get(voice_key, voice_key)
    print(f"[*] Generating voiceover using voice: {voice}")
    print(f"[*] Speed rate: {rate}")
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(out_path)
    print(f"[OK] Voiceover saved to: {out_path} ({os.path.getsize(out_path) / 1024:.1f} KB)")

def main():
    parser = argparse.ArgumentParser(description="Generate Executive Arabic Voiceover")
    parser.add_argument("--text", type=str, help="Text to speak or path to .txt file", required=True)
    parser.add_argument("--voice", type=str, default="saudi_male", choices=list(VOICE_OPTIONS.keys()), help="Voice profile")
    parser.add_argument("--out", type=str, required=True, help="Output mp3 file path")
    parser.add_argument("--rate", type=str, default="+5%", help="Speed rate adjustment (e.g. +5% or 0%)")
    args = parser.parse_args()

    content = args.text
    if os.path.exists(args.text):
        content = Path(args.text).read_text(encoding="utf-8")

    asyncio.run(generate(content, args.voice, args.out, args.rate))

if __name__ == '__main__':
    main()


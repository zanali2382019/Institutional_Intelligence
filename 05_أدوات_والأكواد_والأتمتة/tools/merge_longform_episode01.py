"""
ITQAN Enterprise Intelligence Studio — Master Long-Form Video Merger
Merges 24 cinematic enterprise 16:9 shots with the Master AI Voiceover (voiceover_ep01_master.mp3),
burns synchronized bilingual subtitles (Arabic & English), embeds the permanent watermark '(الذكاء المؤسسي)',
and renders the ultra-compact 720p HD broadcast master video.
"""

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

# Fix console encodings on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def find_ffmpeg() -> str:
    # 1. Shared DreamMatter FFmpeg
    shared_ffmpeg = Path(r"E:\my Office\youtube channel\قناة DreamMatter\مسلسل الاطفال الاحترافي\tools\ffmpeg\ffmpeg.exe")
    if shared_ffmpeg.exists():
        return str(shared_ffmpeg)
    # 2. Local tools FFmpeg
    local_ffmpeg = Path(__file__).resolve().parent / "ffmpeg" / "ffmpeg.exe"
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    # 3. System PATH fallback
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    return "ffmpeg"

def merge_longform_episode01():
    print("=" * 70)
    print("   ITQAN STUDIO — LONG-FORM EPISODE 01 MASTER VIDEO MERGER")
    print("   إتقان — الذكاء المؤسسي")
    print("   كارثة المستخلصات: كيف ابتلع بند خرسانة واحد 12 مليون دولار؟")
    print("=" * 70)

    base_dir = Path(__file__).resolve().parent.parent.parent
    prod_dir = base_dir / "03_الفيديوهات_الطويلة_والشروحات" / "الإنتاج_والمقاطع"
    ffmpeg_exe = find_ffmpeg()

    print(f"\n[*] Using FFmpeg binary: {ffmpeg_exe}")
    print(f"[*] Production directory: {prod_dir}")

    # Look for shots in production dir
    import re
    shots = []
    for i in range(1, 25):
        found = False
        patterns = (
            f"{i}.mp4",
            f"{i:02d}.mp4",
            f"shot{i:02d}.mp4",
            f"shot0{i}.mp4",
            f"shot{i}.mp4",
            f"shot_{i:02d}.mp4",
            f"shot_{i}.mp4",
            f"clip{i:02d}.mp4",
            f"clip{i}.mp4",
            f"video{i:02d}.mp4",
            f"video{i}.mp4",
            f"part{i:02d}.mp4"
        )
        for pattern in patterns:
            candidate = prod_dir / pattern
            if candidate.exists() and "final" not in candidate.name.lower():
                shots.append(candidate)
                found = True
                break
        if not found:
            # Check user Downloads folder as fallback
            user_downloads = Path.home() / "Downloads"
            for pattern in patterns:
                candidate = user_downloads / pattern
                if candidate.exists():
                    dest = prod_dir / f"{i}.mp4"
                    shutil.copy2(candidate, dest)
                    shots.append(dest)
                    print(f"    [+] Imported {candidate.name} from Downloads as {i}.mp4")
                    found = True
                    break

    if not shots:
        all_mp4s = [f for f in prod_dir.glob("*.mp4") if "final" not in f.name.lower()]
        def extract_num(p):
            m = re.search(r'(\d+)', p.stem)
            return int(m.group(1)) if m else 999
        candidates = sorted(all_mp4s, key=extract_num)
        shots = [c for c in candidates if extract_num(c) <= 24]

    if not shots:
        print(f"\n[!] No video clips found in: {prod_dir}")
        sys.exit(1)

    print(f"\n[1/5] Found {len(shots)} video clips:")
    for s in shots:
        print(f"      - {s.name} ({s.stat().st_size / 1024 / 1024:.2f} MB)")

    # Voiceover check
    vo_file = prod_dir / "voiceover_ep01_master.mp3"
    if not vo_file.exists():
        vo_cand = list(prod_dir.glob("*.mp3"))
        if vo_cand:
            vo_file = vo_cand[0]

    if not vo_file or not vo_file.exists():
        print(f"\n[!] Voiceover file not found in: {prod_dir}")
        sys.exit(1)

    print(f"\n[2/5] Master AI Voiceover: {vo_file.name} ({vo_file.stat().st_size / 1024 / 1024:.2f} MB)")

    # Subtitles check
    sub_file = prod_dir / "ep01_bilingual_subtitles.ass"
    if not sub_file.exists():
        print(f"\n[!] Subtitle file not found: {sub_file}")
        sys.exit(1)

    print(f"\n[3/5] Bilingual Subtitles & Watermark: {sub_file.name}")

    # Temp staging for ASCII safety and relative path isolation
    temp_dir = Path(tempfile.gettempdir()) / "itqan_longform_ep01_merge"
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Generate concat list with relative names
        list_lines = []
        for i, s in enumerate(shots, 1):
            dest_name = f"shot_{i:02d}.mp4"
            dest_path = temp_dir / dest_name
            shutil.copy2(str(s), str(dest_path))
            list_lines.append(f"file '{dest_name}'")

        concat_list_file = temp_dir / "concat_list.txt"
        concat_list_file.write_text("\n".join(list_lines), encoding="utf-8")

        temp_audio = temp_dir / "master_audio.mp3"
        shutil.copy2(str(vo_file), str(temp_audio))

        temp_sub = temp_dir / "subtitles.ass"
        shutil.copy2(str(sub_file), str(temp_sub))

        temp_output = temp_dir / "final_output.mp4"
        final_dest = prod_dir / "ITQAN_EP01_CARTHET_AL_MOSTAKHLESAAT_FINAL.mp4"

        print(f"\n[4/5] Rendering Master Video with FFmpeg...")
        print("      - Resolution: 720p HD (1280x720) 16:9 Cinematic Ambient Fill")
        print("      - Watermark: (الذكاء المؤسسي) permanently embedded at Top-Right")
        print("      - Subtitles: Bilingual Arabic & English with Netflix/Bloomberg styling")
        print("      - Compression: Ultra-compact H.264 CRF=25, AAC 128k audio")

        cmd = [
            ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list_file.as_posix()),
            "-i", str(temp_audio.as_posix()),
            "-filter_complex",
            # 1. 720p Ambient Fill: blurred 16:9 background + sharp centered foreground
            # 2. Burn ASS subtitles (bilingual text + continuous watermark badge)
            "[0:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,boxblur=20:5,eq=brightness=-0.2[bg];"
            "[0:v]scale=-1:720[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,ass=subtitles.ass,format=yuv420p[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "25",
            "-c:a", "aac",
            "-strict", "-2",
            "-b:a", "128k",
            "-shortest",
            "-movflags", "+faststart",
            str(temp_output.as_posix())
        ]

        result = subprocess.run(cmd, cwd=str(temp_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("\n[!] FFmpeg Concat Error:")
            print(result.stderr.decode("utf-8", errors="replace")[-1500:])
            sys.exit(1)

        # Move to production folder
        shutil.copy2(str(temp_output), str(final_dest))
        print(f"\n[5/5] SUCCESS! Master Episode 01 rendered successfully:")
        print(f"      -> {final_dest}")
        print(f"      -> Size: {final_dest.stat().st_size / 1024 / 1024:.2f} MB")
        print("=" * 70)
        print("   الحلقة الأولى جاهزة للنشر على YouTube بكامل المواصفات المطلوبة!")
        print("=" * 70)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    merge_longform_episode01()
